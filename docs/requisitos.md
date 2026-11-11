# Especificação de Requisitos — API de Biblioteca

| Versão | Data | Descrição |
|---|---|---|
| 1.0 | 11/11/2026 | Versão inicial — escopo completo (M1 a M5) |

---

## 1. Visão geral

API REST para gerenciar o acervo, os empréstimos, as multas e as reservas de uma biblioteca acadêmica. O sistema não possui interface gráfica: toda a interação ocorre por requisições HTTP, documentadas automaticamente via OpenAPI (Swagger).

### 1.1 Perfis de usuário

| Perfil | Pode |
|---|---|
| **Aluno** | Consultar o acervo; emprestar, renovar e reservar livros; consultar os próprios empréstimos, multas e reservas |
| **Professor** | O mesmo que o aluno, com limites e prazos maiores |
| **Bibliotecário** | Cadastrar usuários e acervo; registrar devoluções, pagamentos de multa e extravios; desativar/reativar contas; consultar dados de todos os usuários. **Não realiza empréstimos** (perfil administrativo) |

### 1.2 Módulos e prioridade de entrega (MoSCoW)

| Módulo | Prioridade |
|---|---|
| M1 — Autenticação e usuários | Must have |
| M2 — Acervo | Must have |
| M3 — Empréstimo | Must have |
| M4 — Devolução e multa | Must have |
| M5 — Renovação e reserva | Should have (implementado por último) |

### 1.3 Fora do escopo do sistema

Interface gráfica, notificações por e-mail, pagamento online de multas e integração com o sistema acadêmico da instituição.

---

## 2. Glossário

| Termo | Definição |
|---|---|
| **Livro** | A obra (título, autor, ISBN). Um livro pode ter vários exemplares |
| **Exemplar** | Cada cópia física de um livro. É o exemplar que é emprestado e possui estado |
| **Empréstimo ativo** | Empréstimo cujo exemplar ainda não foi devolvido nem declarado extraviado |
| **Multa pendente** | Multa gerada e ainda não paga |
| **Reserva ativa** | Reserva nos estados *Na fila* ou *Aguardando retirada* |
| **Dias corridos** | Contagem de dias do calendário, incluindo fins de semana e feriados |

---

## 3. Parâmetros do sistema

Valores centralizados em configuração. Os requisitos referenciam estes parâmetros.

| Parâmetro | Valor |
|---|---|
| Limite de empréstimos ativos — aluno | 3 |
| Limite de empréstimos ativos — professor | 5 |
| Prazo de empréstimo — aluno | 7 dias corridos |
| Prazo de empréstimo — professor | 14 dias corridos |
| Multa por dia de atraso | R$ 1,00 |
| Teto da multa por empréstimo | R$ 30,00 |
| Multa por extravio | R$ 30,00 |
| Máximo de renovações por empréstimo | 2 |
| Máximo de reservas ativas por usuário | 3 |
| Prazo para retirada de exemplar reservado | 2 dias corridos |
| Tamanho da senha | 8 a 20 caracteres |
| Validade do token de acesso | 30 minutos |

---

## 4. Requisitos funcionais

**Criticidade** indica o impacto de uma falha no requisito (Alta / Média / Baixa). Ela orienta a gestão de riscos e define o que é considerado *falha crítica* nos critérios de aceitação.

### M1 — Autenticação e usuários

| ID | Descrição | Criticidade |
|---|---|---|
| RF01 | O bibliotecário cadastra usuários informando nome, e-mail, senha e perfil (aluno, professor ou bibliotecário). | Alta |
| RF02 | A senha deve ter entre 8 e 20 caracteres (inclusive). Fora desse intervalo, o cadastro é recusado. | Média |
| RF03 | O e-mail deve ser único. Cadastro com e-mail já existente é recusado. | Média |
| RF04 | Login com e-mail e senha válidos retorna um token de acesso válido por 30 minutos. | Alta |
| RF05 | Login com credenciais inválidas é recusado com mensagem genérica, sem indicar se o erro está no e-mail ou na senha. | Alta |
| RF06 | Operações protegidas exigem token. Token ausente, inválido ou expirado resulta em recusa por falta de autenticação. | Alta |
| RF07 | Operações administrativas (cadastro de usuários e acervo, devolução, pagamento de multa, extravio, desativação de conta) são exclusivas do bibliotecário. Demais perfis recebem recusa por falta de permissão. | Alta |
| RF08 | Aluno e professor consultam apenas os próprios empréstimos, multas e reservas. Tentativa de acessar dados de outro usuário é recusada. O bibliotecário consulta os dados de todos. | Alta |
| RF09 | O bibliotecário pode desativar e reativar contas. Não é permitido desativar conta com empréstimo ativo. Usuário inativo pode fazer login e consultar, mas não pode emprestar, renovar ou reservar. | Média |

### M2 — Acervo

| ID | Descrição | Criticidade |
|---|---|---|
| RF10 | O bibliotecário cadastra livros com título, autor, ISBN e ano de publicação. O ISBN deve ter exatamente 13 dígitos numéricos e ser único. O ano deve estar entre 1450 e o ano atual (inclusive). | Média |
| RF11 | O bibliotecário cadastra exemplares de um livro existente. Todo exemplar novo inicia no estado *Disponível*. | Média |
| RF12 | Qualquer usuário autenticado pesquisa livros por trecho do título ou do autor, sem diferenciar maiúsculas de minúsculas. | Média |
| RF13 | A consulta de um livro informa a quantidade de exemplares disponíveis. | Baixa |

### M3 — Empréstimo

| ID | Descrição | Criticidade |
|---|---|---|
| RF14 | Aluno ou professor pode emprestar um exemplar somente se **todas** as condições forem atendidas: (a) conta ativa; (b) nenhuma multa pendente; (c) quantidade de empréstimos ativos abaixo do limite do perfil; (d) exemplar *Disponível* — ou *Reservado* para o próprio usuário (ver RF32). A recusa informa qual condição não foi atendida. | Alta |
| RF15 | O limite de empréstimos ativos simultâneos é 3 para aluno e 5 para professor. | Alta |
| RF16 | A data prevista de devolução é a data do empréstimo somada ao prazo do perfil: 7 dias corridos (aluno) ou 14 dias corridos (professor). | Alta |
| RF17 | Ao efetivar o empréstimo, o exemplar passa ao estado *Emprestado*. | Alta |
| RF18 | O bibliotecário não pode realizar empréstimos. | Baixa |

### M4 — Devolução e multa

| ID | Descrição | Criticidade |
|---|---|---|
| RF19 | O bibliotecário registra a devolução de um exemplar emprestado. O empréstimo é encerrado e o exemplar passa a *Disponível* — ou a *Reservado*, se houver fila de reserva para o livro (ver RF32). | Alta |
| RF20 | A devolução de exemplar que não está *Emprestado* é recusada. | Média |
| RF21 | Os dias de atraso correspondem à diferença, em dias corridos, entre a data da devolução e a data prevista. Se o resultado for menor ou igual a zero, não há multa. | Alta |
| RF22 | A multa é de R$ 1,00 por dia de atraso, limitada a R$ 30,00 por empréstimo. | Alta |
| RF23 | Usuário com qualquer multa pendente fica *Bloqueado*. | Alta |
| RF24 | O bibliotecário registra o pagamento de uma multa, sempre pelo valor integral. Quando não restam multas pendentes, o usuário volta a *Ativo*. | Alta |
| RF25 | O bibliotecário pode declarar extravio de um exemplar emprestado: o exemplar passa a *Extraviado* (estado definitivo), o empréstimo é encerrado e o usuário recebe multa de R$ 30,00. | Média |

### M5 — Renovação e reserva

| ID | Descrição | Criticidade |
|---|---|---|
| RF26 | O usuário pode renovar um empréstimo ativo no máximo 2 vezes. | Média |
| RF27 | A renovação só é permitida se o empréstimo não estiver atrasado e não houver reserva ativa para o livro. | Média |
| RF28 | Na renovação, o novo prazo (7 ou 14 dias corridos, conforme o perfil) é contado a partir da data da renovação. | Média |
| RF29 | Só é possível reservar um livro que não tenha nenhum exemplar *Disponível*. | Média |
| RF30 | As reservas formam uma fila por livro, atendida por ordem de chegada (FIFO). | Média |
| RF31 | Cada usuário pode ter no máximo 3 reservas ativas. Usuários bloqueados ou inativos não podem reservar. Não é permitido reservar um livro do qual o usuário já possui exemplar emprestado. | Média |
| RF32 | Quando um exemplar é devolvido e há fila para o livro, ele passa a *Reservado* para o primeiro da fila por 2 dias corridos. Nesse período, somente esse usuário pode emprestá-lo. | Média |
| RF33 | Se o exemplar reservado não for retirado em 2 dias corridos, a reserva expira e o exemplar é reservado para o próximo da fila; se a fila estiver vazia, volta a *Disponível*. | Média |
| RF34 | O usuário pode cancelar a própria reserva enquanto ela estiver ativa. Se havia exemplar separado para ele, aplica-se a mesma regra de RF33. | Baixa |

---

## 5. Máquinas de estado

### 5.1 Exemplar

| Estado atual | Evento | Novo estado |
|---|---|---|
| Disponível | Empréstimo | Emprestado |
| Emprestado | Devolução sem fila | Disponível |
| Emprestado | Devolução com fila | Reservado |
| Emprestado | Extravio | Extraviado |
| Reservado | Empréstimo pelo usuário da vez | Emprestado |
| Reservado | Expiração ou cancelamento, com próximo na fila | Reservado (para o próximo) |
| Reservado | Expiração ou cancelamento, fila vazia | Disponível |
| Extraviado | — | *(estado final)* |

Qualquer combinação estado/evento não listada é uma **transição inválida** e deve ser recusada (ex.: devolver exemplar *Disponível*, emprestar exemplar *Extraviado*).

### 5.2 Usuário

| Estado atual | Evento | Novo estado |
|---|---|---|
| Ativo | Multa gerada | Bloqueado |
| Bloqueado | Última multa pendente paga | Ativo |
| Ativo ou Bloqueado | Desativação (sem empréstimo ativo) | Inativo |
| Inativo | Reativação sem multa pendente | Ativo |
| Inativo | Reativação com multa pendente | Bloqueado |

### 5.3 Reserva

| Estado atual | Evento | Novo estado |
|---|---|---|
| Na fila | Exemplar separado para o usuário | Aguardando retirada |
| Aguardando retirada | Empréstimo realizado | Concluída |
| Aguardando retirada | Prazo de 2 dias esgotado | Expirada |
| Na fila ou Aguardando retirada | Cancelamento pelo usuário | Cancelada |

*Concluída*, *Expirada* e *Cancelada* são estados finais.

---

## 6. Requisitos não funcionais

| ID | Categoria | Descrição |
|---|---|---|
| RNF01 | Desempenho | Com 50 usuários virtuais simultâneos durante 2 minutos (consultas e empréstimos), o percentil 95 do tempo de resposta deve ser inferior a 500 ms e a taxa de erros inferior a 1%. *(meta inicial, revisável após a primeira medição)* |
| RNF02 | Segurança | Senhas armazenadas apenas na forma de hash; nunca em texto puro e nunca retornadas pela API. |
| RNF03 | Segurança | A análise dinâmica (OWASP ZAP) não deve apresentar alertas de risco alto. |
| RNF04 | Segurança | Os parâmetros de entrada, incluindo a busca de livros, não devem permitir injeção de SQL. |
| RNF05 | Consistência | Um exemplar nunca pode estar vinculado a mais de um empréstimo ativo, inclusive sob requisições simultâneas. |
| RNF06 | Usabilidade | Toda resposta de erro retorna JSON com mensagem em português que explica o motivo (ex.: "Limite de 3 empréstimos ativos atingido"). |
| RNF07 | Usabilidade | A API usa códigos HTTP semânticos: 200/201 (sucesso), 401 (não autenticado), 403 (sem permissão), 404 (recurso inexistente), 409 (violação de regra de negócio ou estado), 422 (dados de entrada inválidos). Erros de entrada nunca devem resultar em 500. |
| RNF08 | Usabilidade | Documentação OpenAPI (Swagger) disponível em `/docs`, com descrição de todos os endpoints. |
| RNF09 | Manutenibilidade | Cobertura de testes de pelo menos 80% das linhas e 70% das decisões nos módulos de regra de negócio; quality gate do SonarCloud aprovado. |
| RNF10 | Portabilidade | Executa com Python 3.12+ e SQLite, sem dependência de serviços externos. |
| RNF11 | Testabilidade | A data atual é obtida de um componente substituível (relógio), permitindo testes determinísticos das regras que dependem de data. |

---

## 7. Premissas e restrições

- Um usuário bibliotecário inicial é criado automaticamente na primeira execução.
- Datas são consideradas no fuso America/Sao_Paulo, em dias corridos.
- Não há pagamento parcial de multa.
- Prazo do projeto: apresentação em 16/11/2026, equipe de 4 pessoas.
