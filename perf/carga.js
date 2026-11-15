// Teste de carga da API de Biblioteca (k6)
//
// Como executar, com a API no ar em http://127.0.0.1:8000 e o banco recém-criado:
//   k6 run perf/carga.js
//
// Três cenários, executados em sequência:
//   1. leitura      - 50 usuários virtuais consultando o acervo por 2 minutos (RNF01)
//   2. login        - 10 usuários virtuais fazendo login sem pausa por 30 segundos
//   3. concorrencia - 20 usuários virtuais emprestando o MESMO exemplar ao mesmo tempo (RNF05)

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

const BASE = __ENV.BASE_URL || 'http://127.0.0.1:8000';
const ALUNO = { email: 'aluno@biblioteca.local', senha: 'aluno1234' };
const BIBLIOTECARIO = { email: 'bibliotecario@biblioteca.local', senha: 'biblio1234' };
const JSON_HEADERS = { 'Content-Type': 'application/json' };

// --- Métricas próprias (aparecem no resumo final com estes nomes) ---
const tempoConsulta = new Trend('tempo_consulta', true);
const errosConsulta = new Rate('erros_consulta');
const tempoLogin = new Trend('tempo_login', true);
const errosLogin = new Rate('erros_login');
const emprestimosAceitos = new Counter('emprestimos_aceitos');
const emprestimosRecusados = new Counter('emprestimos_recusados');
const respostasInesperadas = new Counter('respostas_inesperadas');

export const options = {
  scenarios: {
    leitura: {
      executor: 'constant-vus',
      vus: 50,
      duration: '2m',
      exec: 'consultarAcervo',
    },
    login: {
      executor: 'constant-vus',
      vus: 10,
      duration: '30s',
      startTime: '2m10s',
      exec: 'fazerLogin',
    },
    concorrencia: {
      executor: 'per-vu-iterations',
      vus: 20,
      iterations: 1,
      startTime: '2m50s',
      exec: 'emprestarMesmoExemplar',
    },
  },

  // Critérios de aprovação: se algum falhar, o k6 termina com erro
  thresholds: {
    tempo_consulta: ['p(95)<500'], // RNF01: 95% das consultas em menos de 500 ms
    erros_consulta: ['rate<0.01'], // RNF01: menos de 1% de erros
    emprestimos_aceitos: ['count==1'], // RNF05: um exemplar, um único empréstimo
    respostas_inesperadas: ['count==0'], // nenhum erro 500 nem resposta fora do previsto
  },
};

function login(credenciais) {
  return http.post(`${BASE}/auth/login`, JSON.stringify(credenciais), { headers: JSON_HEADERS });
}

function cabecalho(token) {
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
}

// Executado uma vez, antes dos cenários: prepara os dados que eles usam
export function setup() {
  const resposta = login(ALUNO);
  if (resposta.status !== 200) {
    throw new Error(`Login inicial falhou (status ${resposta.status}). A API está no ar?`);
  }
  const token = resposta.json('access_token');

  const alunoId = http.get(`${BASE}/usuarios/eu`, { headers: cabecalho(token) }).json('id');

  const livros = http.get(`${BASE}/livros`, { headers: cabecalho(token) }).json();
  let exemplarId = null;
  for (const livro of livros) {
    for (const exemplar of livro.exemplares) {
      if (exemplar.estado === 'disponivel' && exemplarId === null) {
        exemplarId = exemplar.id;
      }
    }
  }
  if (exemplarId === null) {
    throw new Error('Nenhum exemplar disponível. Apague o arquivo biblioteca.db e suba a API de novo.');
  }

  console.log(`Exemplar disputado no cenário de concorrência: ${exemplarId}`);
  return { token, alunoId, exemplarId };
}

// --- Cenário 1: leitura sob carga sustentada ---
export function consultarAcervo(dados) {
  const resposta = http.get(`${BASE}/livros`, { headers: cabecalho(dados.token) });

  tempoConsulta.add(resposta.timings.duration);
  errosConsulta.add(resposta.status !== 200);
  check(resposta, { 'consulta respondeu 200': (r) => r.status === 200 });

  sleep(1); // tempo de "leitura" do usuário entre uma consulta e outra
}

// --- Cenário 2: logins simultâneos, sem pausa ---
export function fazerLogin() {
  const resposta = login(ALUNO);

  tempoLogin.add(resposta.timings.duration);
  errosLogin.add(resposta.status !== 200);
  check(resposta, { 'login respondeu 200': (r) => r.status === 200 });
}

// --- Cenário 3: disputa pelo mesmo exemplar ---
export function emprestarMesmoExemplar(dados) {
  const resposta = http.post(
    `${BASE}/emprestimos`,
    JSON.stringify({ exemplar_id: dados.exemplarId }),
    {
      headers: cabecalho(dados.token),
      // 201 (aceito) e 409 (recusado pela regra) são respostas previstas aqui
      responseCallback: http.expectedStatuses(201, 409),
    },
  );

  if (resposta.status === 201) {
    emprestimosAceitos.add(1);
  } else if (resposta.status === 409) {
    emprestimosRecusados.add(1);
  } else {
    respostasInesperadas.add(1);
    console.log(`Resposta inesperada: ${resposta.status} ${resposta.body}`);
  }
}

// Executado uma vez, ao final: confere no próprio sistema o estado que ficou gravado
export function teardown(dados) {
  const token = login(BIBLIOTECARIO).json('access_token');
  const emprestimos = http
    .get(`${BASE}/usuarios/${dados.alunoId}/emprestimos`, { headers: cabecalho(token) })
    .json();

  const ativosDoExemplar = emprestimos.filter(
    (e) => e.exemplar_id === dados.exemplarId && e.data_devolucao === null,
  ).length;
  const ativosDoAluno = emprestimos.filter((e) => e.data_devolucao === null).length;

  console.log(`VERIFICACAO RNF05: emprestimos ativos do exemplar ${dados.exemplarId} = ${ativosDoExemplar} (esperado: 1)`);
  console.log(`VERIFICACAO RF15: emprestimos ativos do aluno = ${ativosDoAluno} (limite: 3)`);
}
