# Piloto ALF-like — adução Guandu → entrega às concessionárias

**Data:** 5 de setembro de 2026  
**Origem:** gap analysis IA PUB × CEDAE + matriz Poseidon `06–09` / `matrix.json`.  
**Controle:** SCADA é o único comando; ML em modo **advisory**; LLM fora do laço.

## 1. Objetivo

Detectar e localizar anomalias de vazão/pressão na **adução/macromedição Guandu → pontos de entrega**, no espírito do PUB Anomaly Leak Finder (digital twin hidráulico + ML), **sem** atuar em DMA residencial (mandato das concessionárias).

## 2. Escopo

| Inclui | Exclui |
|---|---|
| Macromedidores Guandu e adutoras com telemetria viva | DMA / AMI residencial |
| PI / historiador; GIS Utility Network se disponível | Varejo Águas do Rio / Iguá / Rio+ |
| Volumes entregues na interface CEDAE × 3 concessionárias | Substituição do SUPERA (evolui a partir dele) |

**SPOF:** Guandu ~45 000 L/s (~80% RM) até Novo Guandu ~mar/2030. What-if Guandu 50% já modelado no Poseidon (cenário 21/07/2026).

## 3. Arquitetura (espelha PUB ALF)

1. Sensores vivos → limpeza / qualidade de dado  
2. **PBS** — simulação física do tronco / adução  
3. **DDP** — baseline ~24 h de vazão/pressão  
4. Detecção de eventos + clusterização → localização aproximada (trecho / ordem de km)  
5. Recalibração diária; alerta ao operador (**zero write-back SCADA**)

## 4. Pré-requisitos (P0)

- Contratos de dado com Águas do Rio / Iguá / Rio+  
- Medição viva (cadastro edital 2021 litigado — não é ground truth sozinho)  
- Barramento produção→entrega (PI/historiador + GIS)

## 5. KPIs de sucesso

- Tempo para detectar anomalia vs baseline manual  
- Taxa de falso positivo acordada com operação  
- Localização útil para campo (trecho / km)  
- Zero atuação automática no SCADA

## 6. Não-objetivos

- Comparar DistLoss PUB 7,2% com SINISA Estado 50,53% na mesma barra (método diferente — ver `09` e campo `method`)  
- Duplicar o COI Águas do Rio — **federar**

## 7. Próximos passos técnicos

1. Inventário de tags PI nos macromedidores Guandu + pontos de entrega  
2. Escolher 1–2 adutoras com densidade de medição  
3. Protótipo DDP+PBS no Poseidon (fixtures primeiro)

## 8. Referências

- `06-benchmark-singapura-pub.md` (ALF / SWG)  
- `09-comparativo-cedae-pub-paris-berlim.md`  
- `10-iaguas-supera-crosswalk.md`  
- Bentley ALF case (PUB); Jacobs Changi twin (modo advisory)
