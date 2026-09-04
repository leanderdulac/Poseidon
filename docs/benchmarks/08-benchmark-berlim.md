# Benchmark Berlim (BWB) × CEDAE — nota breve

**Data da pesquisa:** 2026-09-04 (UTC-3)  
**Operador:** Berliner Wasserbetriebe (BWB) — maior utility municipal de água/esgoto da Alemanha  
**Escopo:** apenas dados **públicos**; cada número tem URL. Detalhe e downloads em `data/berlin/`.

---

## 1. População atendida

| Métrica | Valor | Ano | Fonte |
|---|---|---|---|
| Hab. ligados à água — Berlin | **3.897.100** | 2024 | [EMAS 2025](https://www.bwb.de/de/assets/downloads/Umwelterklaerung-2025.pdf) Tab. 4.1 |
| Hab. ligados à água — Brandenburg | **81.000** | 2024 | idem |
| Hab. ligados ao esgoto — Berlin + BB | **~4,57 Mio** (3.897.100 + 674.000) | 2024 | [EMAS 2025](https://www.bwb.de/de/assets/downloads/Umwelterklaerung-2025.pdf) Tab. 4.2; texto EMAS “~4,6 Mio” |
| População estatística Berlim | **3,914 Mio** | 2025 | [GB 2025](https://www.bwb.de/de/assets/downloads/2025_geschaeftsbericht_berliner_wasserbetriebe.pdf) |

---

## 2. Produção / volumes

| Métrica | Valor | Fonte |
|---|---|---|
| Capacidade dos 9 waterworks | **1.100.000 m³/d** (= **12.731 L/s**) | [Kennzahlen](https://www.bwb.de/de/kennzahlen.php) |
| Demanda média declarada | **~600.000 m³/d** | [Wasserkreislauf](https://www.bwb.de/de/wasserkreislauf.php) |
| Venda de água 2025 | **217 Mio m³/a** (Kennzahlen) / **216,5** (GWF) | [Kennzahlen](https://www.bwb.de/de/kennzahlen.php); [GWF](https://gwf-wasser.de/branche/infrastruktur-staerken-zukunft-sichern/) |
| Esgoto tratado 2025 | **257 Mio m³** | [Kennzahlen](https://www.bwb.de/de/kennzahlen.php); [GWF](https://gwf-wasser.de/branche/infrastruktur-staerken-zukunft-sichern/) |
| Capacidade ETAEs (EMAS) | **673.500 m³/d**; tempo seco até **~721.000 m³/d** | [EMAS](https://www.bwb.de/de/assets/downloads/Umwelterklaerung-2025.pdf); [Wasserkreislauf](https://www.bwb.de/de/wasserkreislauf.php) |
| Rede água / esgoto (2025) | **7.892 km** tubos; **9.788 km** canais; **1.195 km** ADL | [Kennzahlen](https://www.bwb.de/de/kennzahlen.php) |

---

## 3. Perdas / NRW — método

**KPI oficial:** **ILI (Infrastructure Leakage Index)**, não % IWA clássico.

| Ano | ILI | Fonte |
|---|---|---|
| 2024 | **0,92** | [EMAS 2025](https://www.bwb.de/de/assets/downloads/Umwelterklaerung-2025.pdf) Tab. 6 |
| 2023 | 0,86 | idem |
| 2022 | 0,81 | idem |

Referência BWB: ILI **&lt; 1,5** = perdas baixas (europeu).

**Razão volumétrica 2024 (cálculo sobre volumes EMAS):**  
Leitungsverluste Rohrnetz **1.934.860 m³** / Reinwasserverteilung **222,4 Mio m³** = **0,87%**.

**Claims verbais (definições não alinhadas ao 0,87%):** ~**2%** ([press 2021](https://www.bwb.de/de/pressemitteilungen-2021_26781.php)); ~**3%** ([entrevista ZFK / Eva Exner BWB](https://www.zfk.de/wasser-abwasser/wasser/das-rohr-war-noch-nicht-verhaltensauffaellig)).

**Proxy de estado da rede:** Rohrschadensquote **0,07**/km·a (2023) — abaixo do limiar DVGW “baixa” **0,1** ([S19-21195](https://pardok.parlament-berlin.de/starweb/adis/citat/VT/19/SchrAnfr/S19-21195.pdf)); status EMAS 2024 **0,06**.

Para CEDAE: comparar **ILI ou qVR (DVGW W 392)** com BWB; evitar misturar % NRW sem definição.

---

## 4. Tratamento de esgoto / cobertura

- **Anschlussgrad** Berlim **&gt; 99,8%** à rede pública ([S19-10002](https://pardok.parlament-berlin.de/starweb/adis/citat/VT/19/SchrAnfr/S19-10002.pdf); [d19-0668](https://pardok.parlament-berlin.de/starweb/adis/citat/VT/19/DruckSachen/d19-0668.pdf)).  
  → `sewage_treatment_pct` ≈ **99,8%** (população conectada a rede + tratamento central).
- Remoção: **~97%** sólidos/orgânicos biodegradáveis ([Wasserkreislauf](https://www.bwb.de/de/wasserkreislauf.php)); **N 85–88%**, **P &gt;90%** ([entrevista BWB](https://www.bwb.de/de/28580.php)).
- Expansão 4ª/5ª etapa: Flockungsfiltration (P), ozônio/PAC (Spurenstoffe), UV em Ruhleben.

Sistema: **¾ separativo**, **¼ misto** (anel S-Bahn) — risco CSO Spree/Havel.

---

## 5. Qualidade da água

- Medianas **2025** dos 9 waterworks publicadas; BWB afirma conformidade **TrinkwV** ([analysewerte PDF](https://www.bwb.de/de/assets/downloads/analysewerte-wasserwerke.pdf); [Wasserqualität](https://www.bwb.de/de/wasserqualitaet.php)).
- Normalmente **sem desinfecção** (proteção de aquífero / Uferfiltrat).
- Ciclo fechado: **~60%** Uferfiltrat, **30%** chuva, **10%** recarga artificial; **~70%** da água potável influenciada por efluente tratado ([EMAS](https://www.bwb.de/de/assets/downloads/Umwelterklaerung-2025.pdf); [28580](https://www.bwb.de/de/28580.php)).

---

## 6. Digital (CCO / twin / AMI / SCADA)

| Ativo | Evidência pública | Fonte |
|---|---|---|
| **SCADA / Leitsystem** | 3 Leitwarten; modernização **GE iFix** + ACRON; LISA (esgoto) | [Wasserkreislauf](https://www.bwb.de/de/wasserkreislauf.php); [Segno](https://segno.info/wp-content/uploads/2024/11/bericht_bwb.pdf); EMAS |
| **AMI** | 32.946 digitais / 280.785 medidores (2024); meta **100% até 2031** | [EMAS Tab.13](https://www.bwb.de/de/assets/downloads/Umwelterklaerung-2025.pdf) |
| **SEMAplus (IA esgoto)** | Operacional desde **2019** | [KWB SEMAplus](https://kompetenz-wasser.de/de/forschung/dienstleistungen/semaplus) |
| **Leak detection** | AZ-Logger / correlação acústica | [Press 2021](https://www.bwb.de/de/pressemitteilungen-2021_26781.php) |
| **CCO** | **Não** encontrado como marca pública | — |
| **Digital twin city-wide** | **Não** reivindicado no GB/EMAS (há modelos + SCADA + SEMAplus) | — |

---

## 7. Clima — Spree / groundwater

- Fim do lignito na Lausitz → **menos vazão na Spree** → maior fração de efluente tratado nos corpos d’água ([28580](https://www.bwb.de/de/28580.php)).
- Estratégia: Spurenstoffentfernung, Schwammstadt, resiliência à seca/calor ([GB 2025](https://www.bwb.de/de/assets/downloads/2025_geschaeftsbericht_berliner_wasserbetriebe.pdf); [GWF](https://gwf-wasser.de/branche/infrastruktur-staerken-zukunft-sichern/)).
- Investimentos próprios 2025: **543,7 Mio EUR** (rede + obras).

---

## 8. Open Data

| Recurso | URL |
|---|---|
| Portal | https://daten.berlin.de/ |
| Kanalisation 2022 WFS | https://gdi.berlin.de/services/wfs/ua_kanalisation_2022 |
| Catálogo | https://daten.berlin.de/datensaetze/entsorgung-von-regen-und-abwasser-2022-umweltatlas-wfs-e28cdf4f |
| Análises waterworks (catálogo) | https://daten.berlin.de/datensaetze/berliner-wasserbetriebe-wasseranalysedaten-der-wasserwerke |
| GetCapabilities (baixado) | `data/berlin/wfs_ua_kanalisation_2022_GetCapabilities.xml` |

Licença WFS: **dl-de-zero-2.0**. Base: Kanalnetzkarte BWB **10/2022**.

---

## 9. Implicações para benchmark vs CEDAE (Rio)

1. **Perdas:** BWB reporta **ILI ~0,9** e perdas volumétricas de rede **&lt;1%**; claims % 2–3% são secundários. CEDAE deve explicitar método (ILI / IN048 / NRW IWA).  
2. **Cobertura esgoto:** Berlim ~**99,8%** vs déficit típico em RMRJ — gap estrutural.  
3. **Qualidade + ciclo fechado:** Berlim trata e recarrega (Uferfiltrat); pressão climática Spree ≈ stress hídrico para Rio.  
4. **Digital:** SCADA maduro + AMI em ramp-up + IA de ativo (SEMAplus); **sem** CCO/twin “de prateleira” público.  
5. **Open data:** Berlim publica WFS de esgoto; útil como referência de governança de dados.

---

## 10. Desconhecidos (não inventar)

- NRW % IWA oficial único 2024/2025.  
- População servida 2025 desagregada água/esgoto (só 2024 no EMAS).  
- CCO / digital twin oficiais.  
- Cobertura AMI atualizada pós-2024.  
- % exata de CSO / volume de overflow Spree (não extraído neste passe).

Arquivos: `data/berlin/metrics.json`, `data/berlin/SOURCES.md`, PDFs/HTML/XML listados em SOURCES.
