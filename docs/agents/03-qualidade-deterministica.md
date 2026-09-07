# Qualidade determinística — evidência objetiva para agentes F0+

**Data:** 7 de setembro de 2026  
**Escopo:** portões de qualidade **sem LLM no laço**. Agentes F0 (e superiores) usam estes
artefactos como única prova de “código em boa qualidade”.

## Regra dura para agentes

1. **Não se pode afirmar qualidade de código sem portões verdes.**
2. Citação válida = artefactos sob `reports/` (coverage XML/JSON, bandit, mutmut) + saída CI
   (`.github/workflows/quality.yml`).
3. Narrativa / parecer de LLM **não** substitui cobertura, lint, tipos, complexidade ou bandit.
4. Mutação (mutmut) aplica-se aos caminhos críticos de hidráulica / qualidade / ALF / benchmarks;
   não é portão rápido do PR — corre sob `workflow_dispatch` ou `make mutate`.
5. Sem SCADA write. Sem inventar `%` de cobertura.

## Pisos medidos (baseline 2026-09-07)

| Portão | Ferramenta | Limite |
|---|---|---|
| Cobertura | pytest-cov | `fail_under = 90` (TOTAL medido ≈ **91,8%**) |
| Lint | ruff | select E,W,F,I,B,UP,SIM |
| Tipos | mypy | python_version 3.12 (análise; runtime ≥3.11), tipagem gradual |
| Complexidade | xenon/radon | max-absolute **B**, max-modules **A**, max-average **A** |
| Segurança estática | bandit `-ll` | sem issues medium/high |
| Mutação | mutmut | só `hydraulics.py`, `quality.py`, `alf.py`, `benchmarks.py` |

## Makefile

| Alvo | O que faz |
|---|---|
| `make install-dev` | `pip install -e ".[dev]"` |
| `make test` | pytest |
| `make coverage` | pytest --cov + `reports/coverage.*` |
| `make lint` | ruff |
| `make typecheck` | mypy |
| `make complexity` | xenon |
| `make security` | bandit → `reports/bandit.txt` |
| `make mutate` | mutmut nos caminhos críticos (lento) |
| `make quality` | `scripts/quality.sh` (portões rápidos; exit ≠0 se falhar) |

## CI

- **quality.yml** — push/PR para `main`: install `.[dev]`, ruff, mypy, xenon, bandit, pytest --cov.
- **mutation.yml** — `workflow_dispatch` apenas (opcional / lento).

## Como citar

Exemplo aceitável: “`make quality` verde em `<sha>`; coverage TOTAL 91,8% ≥ fail_under 90;
bandit sem findings; xenon B/A/A.”  
Exemplo **inválido**: “o código parece limpo” sem apontar relatório ou CI.

## Caveat mutmut 3.x

`mutmut run` gera cópias sob `mutants/` (gitignored). Em Python 3.14 / mutmut 3.7 o
runner pode falhar a recolher stats se fixtures usarem paths relativos ao CWD
(`data/…`). O smoke `make mutate` / `scripts/mutate.sh` considera **geração** dos
mutantes nos 4 ficheiros críticos como evidência mínima; score completo fica para
`workflow_dispatch` (`.github/workflows/mutation.yml`) após alinhar paths absolutos.
