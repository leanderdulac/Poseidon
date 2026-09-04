# Poseidon — Benchmark Paris (Eau de Paris / SIAAP / STEA) vs CEDAE

**Projeto:** Poseidon (CCO com IA para saneamento no RJ)  
**Data de corte:** 4 de setembro de 2026 (America/Sao_Paulo)  
**Regra:** nenhum número sem URL. Onde falta evidência: **Unknown**.  
**Pacote de dados:** `/workspace/poseidon-cedae/data/paris/` (+ `SOURCES.md`, `metrics.json`)

---

## 1. Arquitetura institucional (não confundir com um único “CEDAE parisiense”)

Desde **1º de janeiro de 2010**, Paris remunicipalizou a água potável. Há **três camadas públicas** distintas:

| Camada | Operador | Escopo |
|---|---|---|
| Água potável | **Eau de Paris** (EPIC / régie) | Captura, tratamento, transporte, distribuição, qualidade, faturação |
| Coleta intramuros | **STEA** (Ville de Paris) | Égouts (~2.500 km), pluviais+usadas, poste de contrôle-commande |
| Transporte + epuração metro | **SIAAP** | ~9,25 M usuários; 6 usinas; ~481 km de emissários/transporte |

Fontes: [paris.fr — Gestion de l’eau](https://www.paris.fr/pages/gestion-de-l-eau-2135); [RPQS 2024](https://cdn.paris.fr/paris/2025/11/28/rpqs-eau-2024-v4-GLFg.pdf); [SIAAP RADD 2024](https://www.siaap.fr/fileadmin/user_upload/Siaap/6_Presse_et_publications/Publication/Editions/institutionnelles/RADD_2024_SIAAP.pdf).

### Veolia / Suez

- **Paris ville:** contratos de distribuição Veolia (rive droite) e Suez (rive gauche) **encerrados** com a remunicipalização → Eau de Paris ([Capital, 2008](https://www.capital.fr/entreprises-marches/veolia-et-suez-evinces-de-paris-pour-la-gestion-de-l-eau-197222); [Livre remunicipalisation](https://www.eaudeparis.fr/sites/default/files/2022-05/LivreRemunicipalisation.pdf)).
- **Ainda operam** pedaços na **grande couronne** (coleta de redevance / distribuição local em communes ligadas ao SIAAP) — listados no [Indicadores SIAAP 2024](https://www.siaap.fr/fileadmin/user_upload/Siaap/6_Presse_et_publications/Publication/Editions/institutionnelles/SIAAP_Indicateurs_RPQS_RA_12_2024.pdf) (ex.: VEOLIA Eau IdF, SUEZ EAU FRANCE). Fora do perímetro “Paris régie”.

**Implicação Poseidon:** o peer útil não é “um operador vertical”; é um **sistema multi-entidade** (produção/distribuição + coleta + WWTP regional) com CCO(s) e contratos de interface — análogo ao RJ pós-concessão (CEDAE atacado + concessionárias).

---

## 2. Tabela-síntese (comparável vs CEDAE / Rio)

| Indicador | Paris (fonte) | Nota metodológica vs BR |
|---|---|---|
| População água | **3 M** usuários/dia (2,2 M parisienes) em 2025 ([RA 2025](https://www.eaudeparis.fr/sites/default/files/2026-07/EDP-RA-2025_web_compressed%20%282%29.pdf)); **2.113.705** habitants desservis 2024 ([RPQS](https://cdn.paris.fr/paris/2025/11/28/rpqs-eau-2024-v4-GLFg.pdf)) | Usuários ≠ habitants desservis |
| População esgoto (metro) | **9,25 M** ([SIAAP RADD 2024](https://www.siaap.fr/fileadmin/user_upload/Siaap/6_Presse_et_publications/Publication/Editions/institutionnelles/RADD_2024_SIAAP.pdf)) | Escala regional, não só Paris |
| Produção potável | **504.759 m³/j** (~**5.842 L/s**); **184,2 Mm³/ano** (2025) ([RA 2025](https://www.eaudeparis.fr/sites/default/files/2026-07/EDP-RA-2025_web_compressed%20%282%29.pdf)) | ~476 mil m³/j em 2024 ([RA 2024](https://www.eaudeparis.fr/sites/default/files/2025-07/EDP_RA2024_WEB.pdf)) |
| Perdas / NRW | Rendement **89%** (2025) → ~**11%** “não rendimento”; **90,9%** (2024) → ~**9,1%** ([RA 2025](https://www.eaudeparis.fr/sites/default/files/2026-07/EDP-RA-2025_web_compressed%20%282%29.pdf); [RPQS](https://cdn.paris.fr/paris/2025/11/28/rpqs-eau-2024-v4-GLFg.pdf)) | **Não** é SINISA. Método = **P104.3** SISPEA ([definição](https://services.eaufrance.fr/indicateurs/P104.3)). ILP 2024: **21,4 m³/km/j** (P106.3). Média FR P104.3 ~**79–83%** (SISPEA/resumo nacional) |
| Tratamento esgoto % (tipo Trata Brasil) | **Unknown** | SIAAP: coleta **conforme** 2024; **P254.3 = 97,3%** (conformidade de *performance* das ETEs — não é % cobertura) ([Indicadores SIAAP](https://www.siaap.fr/fileadmin/user_upload/Siaap/6_Presse_et_publications/Publication/Editions/institutionnelles/SIAAP_Indicateurs_RPQS_RA_12_2024.pdf)) |
| Volume esgoto tratado/recebido | **2.655.371 m³/j** nas 6 usinas; **971,9 Mm³/ano** (2024) ([Indicadores SIAAP](https://www.siaap.fr/fileadmin/user_upload/Siaap/6_Presse_et_publications/Publication/Editions/institutionnelles/SIAAP_Indicateurs_RPQS_RA_12_2024.pdf)) | Comunicação também usa ~2,5 Mm³/j |
| Qualidade água | 2025: **100%** micro / **99,9%** físico-química ([notícia RA](https://www.eaudeparis.fr/en/news/activity-report-2025-sustainable-performance-and-public-service-of-the-future)); 2024 RPQS: P101.1 **100%**, P102.1 **99,9%** | PFAS: conformidade regulatória + ação judicial (mesma notícia) |
| CCO / digital | Eau de Paris: **Centre de pilotage intégré** + Datalab; setorização ~66–67; ~2.500–3.000 sensores acústicos; BIM/jumeau numérique; GTC em renovação ([digital](https://www.eaudeparis.fr/en/thematic-files/the-digital-transformation-of-Paris-water); [distribuer](https://www.eaudeparis.fr/distribuer-leau)). SIAAP: **MAGES** RTC ([página](https://www.siaap.fr/equipements/le-reseau/mages/)). STEA: CCO + **140** estações ([RPQS](https://cdn.paris.fr/paris/2025/11/28/rpqs-eau-2024-v4-GLFg.pdf)) | AMI massivo: **Unknown** |
| Clima | Ceinture intérieure (fase 1 fim 2025→2028); Plan Baignade / Seine; armazenamento SIAAP **>990.000 m³**; rede não potável ~1.700–2.000 km | Peer forte em resiliência urbana + CSO |
| Open data | RPQS anual; SISPEA downloads; fontaines opendata.paris.fr; dashboard usinas SIAAP | Hub'Eau indicadores **descomissiona 10/09/2026** ([aviso](https://www.eaufrance.fr/actualites/decommissionnement-de-lapi-hubeau-indicateurs-des-services-de-leau-et-dassainissement)) |

---

## 3. Perdas — método (obrigatório antes de comparar com CEDAE)

1. França publica **rendement du réseau (P104.3)** = volumes consumidos autorizados (e/ou exportados) ÷ volumes introduzidos na rede.  
2. Converter para “perda %” estilo reportagem: **100 − rendement**. Em 2024: **100 − 90,9 = 9,1%**; em 2025: **100 − 89 = 11%**.  
3. Complementos oficiais: **ILP / P106.3** (perdas em m³/km/j) e **ILVNC / P105.3**.  
4. **Não misturar** com perdas SINISA (Brasil), Ofwat (UK) ou “NRW IWA” sem reconciliar aparências vs reais.

Paris mantém rendimento ~90% com: setorização, debitímetros, **pesquisa acústica contínua**, rede majoritariamente **visitável** em galerias/égouts ([RPQS](https://cdn.paris.fr/paris/2025/11/28/rpqs-eau-2024-v4-GLFg.pdf); [distribuer](https://www.eaudeparis.fr/distribuer-leau)).

---

## 4. Esgoto e qualidade do meio receptor

- STEA coleta **319,8 Mm³** em Paris (2024), rede visitável, **39 déversoirs d’orage** (CSO) ([RPQS](https://cdn.paris.fr/paris/2025/11/28/rpqs-eau-2024-v4-GLFg.pdf)).  
- SIAAP trata em **6 usinas** (Seine Aval/Achères, Seine Valenton, Seine Centre, Seine Grésillons, Marne Aval, Seine Morée).  
- Abatimentos 2024 (todas usinas, dias não excepcionais): DCO **90,6%**, Ptot **83,2%**, NTK **89,6%**, NGL **71,9%** ([Indicadores SIAAP](https://www.siaap.fr/fileadmin/user_upload/Siaap/6_Presse_et_publications/Publication/Editions/institutionnelles/SIAAP_Indicateurs_RPQS_RA_12_2024.pdf)).  
- Herança JO / Plan Baignade: baignade Seine–Marne em 2026 citada no [site SIAAP](https://www.siaap.fr/).

---

## 5. CCO, digital twin, AMI, SCADA — o que está evidenciado

| Ativo | Status | Fonte |
|---|---|---|
| CCO Eau de Paris (ICC) + Datalab | Operacional; ~1M dados/dia | [Digital transformation](https://www.eaudeparis.fr/en/thematic-files/the-digital-transformation-of-Paris-water) |
| Sensores acústicos + setorização | Operacional (meta ~3000; página cita 2500) | [Distribuer l’eau](https://www.eaudeparis.fr/distribuer-leau) |
| GTC / SCADA industrial | Renovação (produção prevista pós-JO / fim 2024) | Mesma página digital |
| Jumeau numérique / BIM | Em implantação (BIM d’Or 2022; LiDAR galerias) | [BIM d’Or](https://www.eaudeparis.fr/en/news/eau-de-paris-winner-of-the-bim-dor-trophies) |
| AMI massivo | **Unknown** (piloto IA de leitura de medidor) | Digital transformation |
| MAGES (SIAAP) | RTC 24h desde ~2008 | [MAGES](https://www.siaap.fr/equipements/le-reseau/mages/) |
| CCO STEA égouts | Poste central + 140 estações | [RPQS](https://cdn.paris.fr/paris/2025/11/28/rpqs-eau-2024-v4-GLFg.pdf) |

---

## 6. Open data utilizável no Poseidon

- **RPQS Ville de Paris** (indicadores oficiais anuais): PDF baixado.  
- **SISPEA** open data nacional (XLS/ODS): https://www.services.eaufrance.fr/pro/telechargement  
- **Fontaines** Eau de Paris: https://opendata.paris.fr/explore/dataset/fontaines-a-boire/ (amostra CSV local).  
- **SIAAP** bilans d’usines (atraso regulatório ~2 meses): https://www.siaap.fr/equipements/tableau-de-bord/bilan-des-usines-depuration/  
- Evitar depender de Hub'Eau indicadores após **10/09/2026**.

---

## 7. Unknowns (não inventar)

- Percentual de tratamento de esgoto **no formato SINISA/Trata Brasil** para Paris/SIAAP.  
- Cobertura AMI / smart metering em massa.  
- Digital twin operacional do STEA (além do CCO clássico).  
- NRW IWA completo (perdas aparentes vs reais) além dos indicadores SISPEA.  
- Série Hub'Eau recente para INSEE 75056 (API v0 retornou anos antigos vazios no corte).

---

## 8. Lições para o Poseidon / CEDAE–RJ

1. **Separar produção/distribuição de coleta/tratamento** na arquitetura de dados do CCO (Paris já é assim).  
2. **Publicar método de perdas** (P104.3 + ILP) — Paris mostra que ~10% é atingível com setorização + acústica + rede visitável; RJ SINISA ~39–50% não é comparável 1:1.  
3. **RTC de esgoto (MAGES)** é o peer de “digital twin hidráulico” para tempo de chuva / CSO — mais próximo de um Poseidon de drenagem/esgoto do que só SCADA de ETA.  
4. **Open data regulatório (RPQS/SISPEA)** reduz assimetria; CEDAE/concessionárias RJ ainda não têm equivalente tão padronizado e anual.

