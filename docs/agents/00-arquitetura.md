# Arquitetura de agentes — atendimento + decisão (Poseidon)

**Data:** 7 de setembro de 2026  
**Escopo:** agentes de IA para (1) apoio à decisão de gestores e (2) atendimento.  
**Fora do núcleo:** [google/mantis](https://github.com/google/mantis) (AppSec) — opcional só em VM isolada sobre o *código*, nunca no CCO.

## Princípios

1. SCADA é o único comando; agentes **leem** (API Poseidon / PI) e **aconselham**.
2. GenAI fora do laço de controle (`llm_no_laco` / `scada_write: false` no `/health`).
3. Federar COI das concessionárias — não duplicar SWG de varejo.
4. Perdas só com campo `method` (SINISA | DistLoss | ILI | SISPEA P104).
5. Auditoria completa: quem perguntou, tools, args, resposta, citations.

## Dois planos, um gateway

| Plano | Usuário | Escrita permitida |
|---|---|---|
| Gestores (F1+) | Operação / diretoria | Nenhuma em campo; só leitura + what-if demo |
| Atendimento (F2) | Cidadão / call center | CRM (ticket) — nunca SCADA |

Ver:

- `01-f0-f1-gateway-gestores.md`
- `02-f2-atendimento.md`

## Roadmap

| Fase | Entrega |
|---|---|
| **F0** | Tool gateway allowlist + RAG + auditoria |
| **F1** | Agentes gestores: situação, PSA, briefing |
| **F2** | Atendimento: triagem + status (+ OS em 2b) |
| **F3** | Anomalia Guandu advisory (DDP+PBS; ver `benchmarks/11`) |
| **F4** | Federação read-only COI Águas do Rio / Iguá / Rio+ |

## Relação com benchmarks

- PSA / qualidade: `benchmarks/12-fusao-iaguas-cma-psa.md` + `src/poseidon/quality.py`
- ALF-like: `benchmarks/11-piloto-alf-guandu.md` + `/api/v1/alf/*`
- Peers: `benchmarks/06–10` + `/api/v1/benchmarks`
