# F2 — Atendimento (cidadão / call center)

**Data:** 7 de setembro de 2026  
**Isolamento:** plano separado do laço hidráulico; compartilha policy/auditoria do F0, **não** tools de what-if hidráulico com o cidadão.

## Agentes

| Agente | Responsabilidade | Tools | Escrita |
|---|---|---|---|
| Triagem | Intent, urgência, município → dono (CEDAE atacado vs concessionária) | Classificador + tabela de cobertura | Não |
| Protocolo / status | Consulta andamento | CRM read | Não |
| Reclamação / OS | Abre chamado | CRM create | **Sim** (só CRM) |
| Escalonamento | Handoff humano | Fila + pacote de contexto | Não |

## Fluxo MVP (F2a)

1. Canal (WhatsApp / portal / 0800) → orquestrador F2  
2. Triagem → se **status** → Protocolo; se **nova reclamação** → Reclamação (F2b) ou humano  
3. Se risco sanitário / falta prolongada / contaminação → **Escalonamento imediato** (sem bot improvisando)

## Regras de negócio

1. Varejo (ligação predial, hidrômetro, rua) → direcionar **Águas do Rio / Iguá / Rio+** conforme município; CEDAE atacado não “abre OS de ponta”.
2. Agente **não** lê SCADA. Opcional: `GET /api/v1/incidents` só para “há incidente conhecido na região?” com disclaimer de demo até live.
3. Prazos só de política CRM publicada — nunca inventados pelo LLM.
4. PII minimizado nos logs (hash/token de protocolo).

## Integrações (a plugar)

| Sistema | Uso | Status típico |
|---|---|---|
| CRM / SAC | Protocolo, OS | A definir (contrato) |
| Tabela de cobertura municipal | Roteamento concessionária | Estática v1 |
| Poseidon `/incidents` | Contexto operacional leve | Demo hoje |
| Base FAQ | RAG atendimento | Separada da KB gestores |

## Critérios de pronto F2a

- [ ] Triagem acerta dono (CEDAE vs concessionária) em golden set
- [ ] Status protocolo end-to-end em sandbox CRM
- [ ] Escalamento humano < N segundos em intent crítico
- [ ] Zero chamada a `/hydraulics/*` ou `/alf/*` a partir do plano cidadão

## F2b (depois)

- Abertura de OS com anexos
- Notificação proativa de incidente (opt-in)
- Pesquisa de satisfação pós-atendimento
