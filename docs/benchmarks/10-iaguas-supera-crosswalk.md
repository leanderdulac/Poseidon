# Crosswalk IAguas / SUPERA × PUB / Paris / Berlim

**Data:** 5 de setembro de 2026  
**Origem:** cruzamento com IA PUB (Singapura) + matriz Poseidon `docs/benchmarks/06–09` e `data/comparison/matrix.json`.  
**Regra:** não cruzar % de perdas entre métodos (SINISA ≠ DistLoss ≠ ILI ≠ SISPEA P104.3).

## 1. Onde cada peça da CEDAE se encaixa

| Ativo CEDAE | Função | Peer mais próximo | Gap | Ação Poseidon |
|---|---|---|---|---|
| **IAguas** (Finep 2025; VM9/NOAH/UFF) | Anomalia em manancial + alerta prévio (~7 d) | PUB sensores WQ/flood; CMA Botafogo | Já é frente forte; falta fusão no PSA da parede | **P1:** timeline único CMA + IAguas + lab geosmina/2-MIB + PSA |
| **CMA Botafogo** (jun/2026) | Vigilância 24h Guandu / Guapiaçu–Macacu | PUB catchment sensors; Eau de Paris ICC (parcial) | É manancial, **não** CCO de ciclo | Federar no CCO; não vender como twin de rede |
| **SUPERA** (desde ~2016) | IoT + algoritmos + painel geo de perdas reais/aparentes | Paris acústica (2,5–3k); PUB ALF (abaixo) | Dashboard/telemetria; fraco em gêmeo hidráulico NRT física+ML | **P1:** evoluir para twin/anomalia na **adução Guandu→entrega** |
| CCOs de ETA + IRM | Operação local / entrega atacado | BWB Leitwarten; PUB IWMS | Fragmentado; IRM com risco de governança | Barramento multi-operador (P0) |
| — (ausente) | Digital twin de adutora / leak localization | **PUB ALF** | Maior gap de perdas/rede no atacado | Piloto ALF-like em macromedição (não DMA residencial CEDAE) |
| — (ausente no atacado) | AMI residencial | PUB ~300k; BWB 33k→100% 2031 | Não é mandato CEDAE pós-concessão | Consumir agregado das 3 concessionárias |
| — (ausente) | RTC esgoto / chuva | **SIAAP MAGES**; BWB SEMAplus | Baixada colapsada | **P2** com concessionárias |
| COI Águas do Rio | CCO urbano (~1,5k unid., 48k tags) | PUB Smart Water Grid | Já existe no RJ — não é da CEDAE | **Federar**, não duplicar |

## 2. Regras do cruzamento

1. **IAguas ≠ ALF.** IAguas = qualidade/manancial. ALF = hidráulica + ML na rede. No Poseidon: IAguas alimenta PSA; ALF-like é outro módulo.
2. **SUPERA → ALF-like** na interface de entrega (volumes produzidos vs recebidos), não em hidrômetro da ponta.
3. **Perdas:** campo `method` obrigatório (`GET /api/v1/benchmarks`). Estado RJ 50,53% SINISA não se plota contra PUB 7,2% DistLoss nem BWB ILI 0,92.
4. **P0 de dados:** contratos com Águas do Rio / Iguá / Rio+ + medição viva. Cadastro edital 2021 litigado — não é ground truth.
5. **Controle:** SCADA único comando; ML advisory; sem genAI no laço (padrão PUB + Poseidon).

## 3. Prioridades (alinhadas)

| Prioridade | Escopo |
|---|---|
| **P0** | Barramento produção→entrega; macromedição; historiador + GIS; contratos de dado |
| **P1** | Fusão IAguas+CMA+lab no PSA; piloto twin/anomalia Guandu→entrega (ALF-like); federar COI Águas do Rio |
| **P2** | Twin advisory Guandu + PdM recalques; RTC Baixada (MAGES/SEMAplus) |

## 4. Referências

- `06-benchmark-singapura-pub.md`, `07-benchmark-paris.md`, `08-benchmark-berlim.md`, `09-comparativo-cedae-pub-paris-berlim.md`
- `data/comparison/matrix.json` → `poseidon_actions`
- Repo: https://github.com/leanderdulac/Poseidon
