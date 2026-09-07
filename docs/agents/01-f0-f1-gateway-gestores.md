# F0 / F1 — Gateway, RAG e agentes gestores

**Data:** 7 de setembro de 2026  
**API de referência:** `src/poseidon/api.py` (demo, bind `127.0.0.1`, consultivo).

## F0 — Base comum

### Tool gateway

Allowlist **somente** dos endpoints Poseidon abaixo. Qualquer outra URL = deny.

| Method | Path | Uso agente |
|---|---|---|
| GET | `/health` | Sanity / flags `scada_write`, `llm_no_laco` |
| GET | `/api/v1/systems` | Lista sistemas RM |
| GET | `/api/v1/psa` | Regime PSA atual |
| GET | `/api/v1/incidents` | Incidentes (fixture → depois live) |
| GET | `/api/v1/demanda` | Forecast demanda (`horizonte_h` clamp 1–48) |
| GET | `/api/v1/benchmarks` | Matriz peers |
| GET | `/api/v1/benchmarks/actions` | `poseidon_actions` |
| GET | `/api/v1/alf/baseline` | Baseline ALF advisory |
| POST | `/api/v1/alf/demo/anomaly` | Demo anomalia |
| POST | `/api/v1/demo/geosmina` | What-if qualidade |
| POST | `/api/v1/demo/guandu-50` | What-if SPOF Guandu |
| POST | `/api/v1/hydraulics/hammer` | Golpe de aríete (consultivo) |
| POST | `/api/v1/hydraulics/headloss` | Perda de carga (consultivo) |

**Proibido no gateway:** write SCADA, shell, Mantis reproduce/patch, credenciais de concessionária sem contrato.

### RAG

Indexar (com `source_id` estável):

- `docs/benchmarks/06` … `12`
- Playbooks PSA internos (quando existirem)
- FAQ operacional gestores (curto)

Resposta do LLM **deve** citar `source_id` ou `recurso` da tool. Número sem tool/RAG = inválido.

### Auditoria

Campos mínimos por turno: `timestamp`, `actor_id`, `role`, `intent`, `tools[]`, `args`, `latency_ms`, `answer_hash`, `citations[]`.

## F1 — Agentes gestores

### Router de intent

Exemplos: `situacao` | `psa` | `guandu` | `perdas_bench` | `briefing` | `hidraulica`.

### Agente Situação

1. `GET /systems`, `GET /incidents`, `GET /demanda`
2. Resume desvios em português claro
3. Não inventa vazão L/s

### Agente PSA

1. `GET /psa`
2. Opcional: `POST /demo/geosmina` para cenário
3. Alinha narrativa às camadas do doc 12 (CMA → IAguas → lab → PSA → humano)
4. Usa limiares de `quality.classificar_psa` (0,02 / 0,1 µg/L) — lab, não sensor ng/L online

### Agente Briefing

1. Chama Situação + PSA (+ `benchmarks/actions` se pedido)
2. Emite markdown ≤1 página: o que aconteceu, risco, próxima ação **humana**
3. Marca `meta.live=false` enquanto fixtures

### Critérios de pronto F1

- [ ] Gateway deny-by-default testado
- [ ] Briefing diário gerado só com tools allowlist
- [ ] Trace auditável por pergunta
- [ ] UI/dashboard consome o mesmo JSON que o agente

## Fora de F1

- Atendimento cidadão → F2
- Twin adução produção com tags PI reais → F3 (após fixtures DDP+PBS)
- Feeds COI → F4
