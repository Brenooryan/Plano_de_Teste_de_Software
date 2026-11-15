"""Resume o resultado do scan de segurança e aplica o quality gate (RNF03 e RNF07).

Uso:
    python scripts/resumo_seguranca.py <relatorio-zap.json> <uvicorn.log>

Lê duas fontes:
  1. o relatório JSON do OWASP ZAP, com os alertas encontrados;
  2. o log de acesso da API, com a resposta dada a cada requisição do scan.

Termina com erro (código 1) se houver alerta de risco alto ou resposta 5xx.
"""

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

NOMES_DE_RISCO = {"3": "Alto", "2": "Médio", "1": "Baixo", "0": "Informativo"}
RISCO_ALTO = "3"

# Exemplo de linha: INFO:     127.0.0.1:41234 - "GET /livros HTTP/1.1" 200 OK
LINHA_DE_ACESSO = re.compile(r'"(?P<metodo>[A-Z]+) (?P<caminho>\S+) HTTP/[\d.]+" (?P<status>\d{3})')


def ler_alertas(caminho: Path) -> list[dict]:
    """Devolve os alertas do relatório do ZAP, do risco mais alto para o mais baixo."""
    relatorio = json.loads(caminho.read_text(encoding="utf-8"))

    sites = relatorio.get("site", [])
    if isinstance(sites, dict):
        sites = [sites]

    alertas = []
    for site in sites:
        for alerta in site.get("alerts", []):
            alertas.append(
                {
                    "risco": str(alerta.get("riskcode", "0")),
                    "nome": alerta.get("alert") or alerta.get("name", "(sem nome)"),
                    "ocorrencias": len(alerta.get("instances", [])),
                    "cwe": str(alerta.get("cweid", "")),
                }
            )

    return sorted(alertas, key=lambda a: (-int(a["risco"]), a["nome"]))


def ler_acessos(caminho: Path) -> tuple[Counter, list[str]]:
    """Conta as respostas da API por código HTTP e separa as linhas com erro 5xx."""
    por_status: Counter = Counter()
    erros_do_servidor = []

    for linha in caminho.read_text(encoding="utf-8", errors="replace").splitlines():
        achado = LINHA_DE_ACESSO.search(linha)
        if achado is None:
            continue
        status = achado["status"]
        por_status[status] += 1
        if status.startswith("5"):
            erros_do_servidor.append(f"{achado['metodo']} {achado['caminho']} -> {status}")

    return por_status, erros_do_servidor


def montar_resumo(alertas: list[dict], por_status: Counter, erros: list[str]) -> str:
    linhas = ["## Scan de segurança (OWASP ZAP)", ""]

    por_risco = Counter(a["risco"] for a in alertas)
    linhas += ["### Alertas por nível de risco", "", "| Risco | Tipos de alerta |", "|---|---|"]
    for codigo in ("3", "2", "1", "0"):
        linhas.append(f"| {NOMES_DE_RISCO[codigo]} | {por_risco.get(codigo, 0)} |")

    linhas += ["", "### Alertas encontrados", ""]
    if alertas:
        linhas += ["| Risco | Alerta | Ocorrências | CWE |", "|---|---|---|---|"]
        for a in alertas:
            risco = NOMES_DE_RISCO.get(a["risco"], a["risco"])
            linhas.append(f"| {risco} | {a['nome']} | {a['ocorrencias']} | {a['cwe']} |")
    else:
        linhas.append("Nenhum alerta.")

    total = sum(por_status.values())
    linhas += ["", f"### Respostas da API durante o scan ({total} requisições)", ""]
    linhas += ["| Código HTTP | Quantidade |", "|---|---|"]
    for status in sorted(por_status):
        linhas.append(f"| {status} | {por_status[status]} |")

    if erros:
        linhas += ["", f"### Requisições que causaram erro no servidor ({len(erros)})", ""]
        linhas += [f"- `{erro}`" for erro in erros[:30]]
        if len(erros) > 30:
            linhas.append(f"- ... e mais {len(erros) - 30}")

    return "\n".join(linhas)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    alertas = ler_alertas(Path(sys.argv[1]))
    por_status, erros = ler_acessos(Path(sys.argv[2]))

    resumo = montar_resumo(alertas, por_status, erros)
    print(resumo)

    # No GitHub Actions, o mesmo resumo aparece na página da execução
    arquivo_de_resumo = os.environ.get("GITHUB_STEP_SUMMARY")
    if arquivo_de_resumo:
        with open(arquivo_de_resumo, "a", encoding="utf-8") as saida:
            saida.write(resumo + "\n")

    alertas_altos = sum(1 for a in alertas if a["risco"] == RISCO_ALTO)
    print()
    if alertas_altos or erros:
        print(f"QUALITY GATE REPROVADO: {alertas_altos} alerta(s) de risco alto, "
              f"{len(erros)} resposta(s) 5xx.")
        return 1

    print("QUALITY GATE APROVADO: nenhum alerta de risco alto e nenhuma resposta 5xx.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
