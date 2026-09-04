# Comparativo CEDAE × PUB (Singapura) × Paris × Berlim

**Data:** 4 de setembro de 2026  
**Regra:** números só com fonte nos briefs `06`–`08` e JSONs em `data/`. Métodos de perda **não** são intercambiáveis.

## 1. Tabela-síntese

| | CEDAE / RJ | PUB Singapura | Paris (Eau de Paris + SIAAP) | Berlim (BWB) |
|---|---|---|---|---|
| Papel | Atacado RM + ciclo em ~15 mun. | Utilidade nacional integrada | Água = EDP; esgoto = STEA+SIAAP | Utilidade integrada (água+esgoto) |
| População | Guandu >9 mi; sistemas RM ~12 mi | 6,11 mi (100%) | EDP ~3 mi; SIAAP ~9,25 mi | ~4,57 mi (esgoto 2024) |
| Produção / vendas | Guandu **45 000 L/s**; Laranjal 7 000 | Vendas ~**21 209 L/s** (potável+NEWater 2025) | EDP ~**5 842 L/s** (2025) | Capacidade **12 731 L/s**; vendas ~6 876 L/s |
| Perdas (valor) | Estado **50,53%**; mun. RJ **38,92%** | **7,2%** (CY2025) | ~**11%** (rendimento 89%, 2025) | ILI **0,92**; volume **0,87%** |
| Método de perda | SINISA % distribuição | Distribution Losses % | SISPEA P104.3 (100−rendimento) | ILI (DVGW/IWA) + volume EMAS |
| Esgoto tratado | Atacado não; Baixada colapsada (Meriti 0%) | **100%** | SIAAP P254.3 **97,3%** (2024) | Ligação **>99,8%** |
| Digital | CMA 2026 (manancial); sem gêmeo de adutora público | SWG + **ALF** twin + 1 500 sensores + AMI ~300k | ICC/Datalab; **MAGES** RTC; ~2,5–3k acústicos | 3 Leitwarten; SEMAplus; AMI 33k→100% 2031 |
| SPOF de produção | Guandu ~80% até Novo Guandu 2030 | Four National Taps (diversificado) | Ceinture + múltiplas usinas | 9 waterworks; Uferfiltrat |

## 2. O que dá para comparar de verdade

| Tema | Comparável? | Como usar no Poseidon |
|---|---|---|
| Capacidade / vazão (L/s, m³/d) | **Sim** | Normalizar tudo para L/s. Guandu sozinho > PUB vendas + Paris + Berlim capacidade. |
| Cobertura de esgoto / tratamento | **Parcial** | PUB/BWB/SIAAP ≈100%; CEDAE atacado não carrega o KPI — comparar concessionárias RJ vs peers. |
| Perdas % cruzadas | **Não direto** | Guardar quatro campos: `sinisa_pct`, `sispea_p104`, `ili`, `dist_loss_pct` + `method`. Nunca plotar 0,87 vs 50 na mesma barra sem nota. |
| ILI | **Sim se CEDAE/concessionárias calcularem** | Berlim é o padrão. Meta Poseidon: calcular ILI na interface de entrega. |
| Digital twin / leak localization | **Sim (qualitativo + arquitetura)** | Copiar lógica ALF (PUB) e setorização acústica Paris; não o marketing. |
| RTC de esgoto / chuva | **Sim** | MAGES (SIAAP) + SEMAplus (BWB) → DSS de chuva Baixada no Poseidon. |
| AMI residencial | **Não para CEDAE atacado** | Consumir agregado das concessionárias (padrão Paris/Berlim). |
| Diversidade de manancial | **Sim** | Four Taps / multi-ETA vs Guandu SPOF → “Novo Guandu virtual” já no modelo. |
| Open data GIS | **Sim** | WFS Berlim + open data Paris como referência de camada GIS do CCO. |

## 3. Lacunas (unknown)

- NRW oficial da CEDAE residual (atacado) e ILI RJ.
- L/lig·dia para PUB e Paris (só RJ tem no SINISA).
- AMI consolidado das três concessionárias RJ.
- CCO único metropolitano no RJ (CMA ≠ CCO ciclo).

## 4. O que entra agora no Poseidon

1. Módulo `benchmarks` com a matriz JSON e validação de método.
2. Documentar no README que perdas só entram com `method`.
3. Priorizar features inspiradas nos peers: (a) gêmeo de anomalia tipo ALF na adução Guandu; (b) RTC/chuva tipo MAGES na Baixada; (c) ILI na interface CEDAE–concessionárias.
4. Manter fixtures CEDAE; peers são referência, não telemetria.

## 5. Fontes

- `06-benchmark-singapura-pub.md` + `data/singapore/`
- `07-benchmark-paris.md` + `data/paris/`
- `08-benchmark-berlim.md` + `data/berlin/`
- `01-cedae-operacao.md`, `02-benchmarks.md`
- `data/comparison/matrix.json`
