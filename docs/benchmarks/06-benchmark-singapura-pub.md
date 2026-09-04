# Benchmark PUB Singapura × CEDAE (Rio) — dados públicos

**Data da pesquisa:** 2026-09-04  
**Operador:** PUB (Public Utilities Board), agência nacional de água de Singapura  
**Escopo:** métricas comparáveis para o projeto Poseidon/CEDAE. **Nenhum número foi inventado** — cada cifra cita URL/fonte.

Arquivos baixados: `/workspace/poseidon-cedae/data/singapore/`  
Índice de fontes e licenças: `data/singapore/SOURCES.md`  
JSON estruturado: `data/singapore/metrics.json`

---

## 1. População e conexões

| Métrica | Valor | Ano | Fonte |
|---|---|---|---|
| População total de Singapura | **6.111.200** (6,11 milhões) | fim-jun/2025 | [Population in Brief 2025](https://www.population.gov.sg/files/media-centre/publications/Population_in_Brief_2025.pdf); [SingStat](https://www.singstat.gov.sg/find-data/explore-data-themes/population/population-and-population-structure/latest-news-data) |
| População com água encanada + saneamento moderno | **100%** | CY 2022–2024 | [PUB ASR 2024/25](https://www.pub.gov.sg/-/media/PUB/Publications/Report/PDF/PUB_ASR_2025.pdf) (métricas GRI) |
| Contas / conexões servidas | **~1,7 milhão** de residências e negócios | fev/2025 | [Press release PUB](https://www.pub.gov.sg/Resources/News-Room/PressReleases/2025/02/Keeping-Singapore-potable-water-pipe-network-in-good-order) |
| Rede potável | **~6.000 km** | 2025 | Idem |

**Implicação CEDAE:** PUB é utilitário nacional de cidade-estado (100% cobertura). Comparar cobertura e NRW em % é justo; comparar escala absoluta (Rio metropolitano vs. ~6 mi hab.) exige normalização por conta/km/população.

---

## 2. Produção / demanda de água

| Métrica | Valor | Unidade | Fonte |
|---|---|---|---|
| Demanda total declarada | **~440 mgd** (“about”) | milhões de galões/dia | [PUB Water Loop](https://www.pub.gov.sg/Public/WaterLoop) |
| Vendas água potável | **515,5** | Mm³/ano (2025) | [SingStat Water Sales](https://data.gov.sg/datasets/d_9db4902c7a47357441dac7d2806032a5/view) — unidade oficial: *Million Cubic Metres Per Year* |
|  doméstico | 304,4 | Mm³/ano (2025) | Idem |
|  não doméstico | 211,1 | Mm³/ano (2025) | Idem |
| Vendas NEWater | **153,8** | Mm³/ano (2025) | Idem + [NEWater sold](https://data.gov.sg/datasets/d_2eceeb792a0fca1caa74304d47b46060/view) |
| Vendas potável + NEWater (derivado) | **≈ 1,83 Mm³/d** (~21.200 L/s) | m³/d | Cálculo: (515,5+153,8)×10⁶ / 365,25 |
| Consumo doméstico per capita | **142 LPCD** | L/pessoa·dia (CY 2024) | PUB ASR 2024/25 (meta Green Plan 2030: 130 LPCD) |

**Nota metodológica:** vendas ≠ produção. A produção inclui perdas de distribuição. A cifra “~440 mgd” é aproximada na página PUB; SingStat dá volumes anuais auditáveis. Não foi encontrado no portal aberto um único arquivo com **produção bruta** diária em m³/d.

---

## 3. NRW / perdas de água

| Ano (calendário) | Distribution Losses (%) | Fonte |
|---|---|---|
| 2022 | 7,5 | PUB ASR 2024/25 (GRI) |
| 2023 | 7,2 | Idem |
| 2024 | 7,1 | Idem |
| **2025** | **7,2** | [Resposta parlamentar MSE, 8 abr 2026](https://www.mse.gov.sg/latest-news/written-reply-to-parliamentary-question-on-water-loss-rate-in-the-national-water-distribution-system-in-2025/) |

**Método:** indicador oficial **“% of Distribution Losses”** na rede potável. Desde 2019 substituiu “Unaccounted for Water” por ser “mais holístico” (inclui todos os vazamentos possíveis) — nota 2 do ASR. **Não** foi encontrado valor público em **L/conexão·dia** (ILI/IWA detalhado).

**Operação de vazamentos (2024):** 267 reparos ≈ **4,5 vazamentos / 100 km·ano** (era 5,7 em 2014); <10% interrompem o abastecimento; restauro médio em ~4 h após isolamento ([press release](https://www.pub.gov.sg/Resources/News-Room/PressReleases/2025/02/Keeping-Singapore-potable-water-pipe-network-in-good-order)).

---

## 4. Esgoto — coleta e tratamento

| Métrica | Valor | Fonte |
|---|---|---|
| Acesso a saneamento melhorado / moderno | **100%** | data.gov.sg acesso água/saneamento; PUB ASR |
| Águas residuais domésticas tratadas com segurança | **100%** (2024) | [SDG 6 Data — Singapore](https://sdg6data.org/en/country-or-area/Singapore) (indicador 6.3.1) |
| Arquitetura | Rede de esgotos + **Deep Tunnel Sewerage System (DTSS)** → Water Reclamation Plants → NEWater | PUB ASR / MSE Water Policy |
| Capacidade exemplo | Expansão Changi WRP Fase 2: de **202 → 246 mgd** de tratamento de used water | PUB ASR 2024/25 |
| Interrupções em esgoto | ~9,7–9,9 por mês por 1.000 km de esgotos (CY 2022–24) | PUB ASR GRI |

Código de prática: `cop_sewerage_sanitary_2025.pdf` (3ª ed., mar 2025).

---

## 5. Qualidade e monitoramento

- **100%** dos testes atendendo diretrizes WHO / EPH para água potável (CY 2022–2024) — PUB ASR.
- Dataset aberto 2023–2025: `Drinkingwaterqualitydatasets.csv` — ex.: *E. coli* 2025 média e faixa **&lt;1 cfu/100 mL**; turbidez média 0,15 NTU ([data.gov.sg](https://data.gov.sg/datasets/d_f397c39929978d3047e0e32430c6763b/view)).
- Incidentes de qualidade com interrupção em massa **não** aparecem como série pública de “outbreaks”; o material público enfatiza conformidade contínua e enforcement contra danos à rede (ex.: 6 empreiteiros processados em 2024 por dano a tubos).

---

## 6. Ativos digitais (Smart Water / ALF / AMI / SCADA)

| Ativo | Evidência pública | Fonte |
|---|---|---|
| **Smart Water Grid (SWG)** | Monitoramento da rede de ~6.000 km | Bentley case study; ASR/AR históricos |
| **ALF (Anomaly Leak Finder)** | Digital twin de alta fidelidade + IA/ML; recalibração diária; localização &lt;1 km; cloud comercial do governo | [Bentley PDF](https://www.bentley.com/wp-content/uploads/cs-pub-digital-anomaly-ltr-en-lr.pdf); [YII Bentley](https://yii.bentley.com/project/high-fidelity-digital-twin-enabled-anomaly-detection-and-localization-in-singapore/) |
| Sensores acústicos permanentes | **1.500** | Press release PUB fev/2025 |
| **AMI / Smart Water Meters** | Fase 1 **~300.000** medidores; portal MySmartWaterMeter (horário/diário + alertas de vazamento) | [PUB Smart Water Meter](https://www.pub.gov.sg/Public/KeyInitiatives/Smart-Water-Meter) |
| **SCADA** | Ambiente SCADA operacional existente (referenciado em materiais de digital twin) | Detalhe público limitado no site PUB |
| GPS / geofencing de máquinas | Obrigatório desde 2023 perto de dutos críticos | MSE reply 2026; Sustainability Report 2023 |
| Analytics de esgoto | Sewer Analytics and Management System; sensores VOC / microbianos | PUB SR 2023 |
| **CCO** | Termo **não usado** pela PUB; controle operacional via SCADA/SWG/ALF/monitoramento de cheias | — |

**Atenção:** matérias de trade media (2026) sobre “Digital Aqua Phase II / tenders” **não foram confirmadas** em pub.gov.sg e apresentam cifras conflitantes — **não** usadas neste benchmark.

---

## 7. Resiliência climática (seca / cheia)

- **Four National Taps:** captação local (2/3 do território; 17 reservatórios; ~8.000 km de drenos), importação Johor (acordo até 2061, até 250 mgd), **NEWater**, **dessalinização** (5 plantas) — [MSE Water](https://www.mse.gov.sg/policies/water/).
- NEWater e dessalinização tratados como fontes **resilientes ao clima** (independentes da chuva).
- Cheias: abordagem **Source–Pathway–Receptor**; hotspots de inundação CY2022–24: **26 → 23 → 22**; Flood Resilience Cluster criado em **1 ago 2025** (PUB ASR).
- **2026 = Year of Climate Adaptation** ([MSE YOCA](https://www.mse.gov.sg/yoca/)); Plano Nacional de Adaptação previsto para 2027.
- Alertas: sensores de nível, CCTV, app **myENV**, Telegram PUB.

---

## 8. Portais / datasets efetivamente baixáveis

| Dataset | Formato local | Licença |
|---|---|---|
| Water Sales, Annual | `WaterSalesAnnual.csv` | [Open Data Licence v1.0](https://data.gov.sg/open-data-licence) |
| Volume of NEWater sold | `VolumeofNEWatersoldAnnual.csv` | Idem |
| Drinking water quality | `Drinkingwaterqualitydatasets.csv` | Idem |
| Access water & sanitation by region | `AccessTo….csv` | Idem |
| Relatórios PUB (ASR, AR, SR, Green Bond, COP) | PDFs em `data/singapore/` | © PUB — citação |
| Population in Brief 2025 | PDF | Governo SG |

Portal: [https://data.gov.sg](https://data.gov.sg) (buscar “PUB”, “water sales”, “drinking water quality”).

---

## 9. O que **não** foi encontrado (público)

- Valor oficial de perdas em **L/conexão·dia** ou ILI IWA completo.
- Série aberta de **produção bruta** diária (apenas vendas anuais + “~440 mgd”).
- Número exato atualizado de contas AMI instaladas além da meta/fase 1 (~300 mil) — sem dashboard público de progressão 2025/26.
- Termo/estrutura **CCO** equivalente à nomenclatura brasileira.
- Contagem pública de “incidentes de qualidade” tipo outbreak (só conformidade WHO 100% + casos de dano a rede).
- Confirmação oficial em pub.gov.sg dos tenders “Digital Aqua Phase II” reportados por trade media em 2026.
- PDF Population Trends SingStat `.ashx` retornou 404 no download automático (cifras confirmadas via Population in Brief + SingStat web).

---

## 10. Leituras rápidas para Poseidon × CEDAE

1. **NRW:** PUB ~**7%** (Distribution Losses) vs. tipicamente dezenas de % em utilities brasileiras — método diferente; alinhar definição antes de comparar.
2. **Digital:** PUB já opera **SWG + ALF (digital twin) + AMI parcial + 1.500 sensores** — referência de maturidade, não de escala territorial.
3. **Esgoto fechado no ciclo:** 100% tratamento + NEWater é o diferencial estrutural (economia circular da água).
4. **Clima:** diversificação de fontes + drenagem urbana + adaptação costeira — paralelo útil para seca/cheia no Rio.
5. **Dados abertos:** Singapura publica vendas, qualidade e indicadores ASR; não publica SCADA bruto nem NRW em L/conn·dia.

---

*Documento gerado para o workspace poseidon-cedae. Atualizar métricas quando o próximo ASR PUB (pós-2025) e novos datasets data.gov.sg forem publicados.*
