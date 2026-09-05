# Fusão IAguas / CMA no timeline PSA (Guandu & Imunana-Laranjal)

**Data:** 5 de setembro de 2026  
**Código relacionado:** `src/poseidon/quality.py` (`classificar_psa`, ADE geosmina/2-MIB)

## 1. Contexto

| Peça | Papel |
|---|---|
| **IAguas** (Finep 2025; VM9/NOAH/UFF) | IA de anomalia em manancial + alerta prévio (~7 dias) |
| **CMA Botafogo** (jun/2026) | Vigilância 24h Guandu / Guapiaçu–Macacu — câmeras, boias, drones; **não** é CCO de ciclo |
| Eventos recentes | Geosmina 2021; tolueno Laranjal 2024 (origem aberta) |
| Poseidon | ADE + limiares PSA; proxy ficocianina; **não existe** sensor online ng/L → lab |

## 2. Objetivo

Um **timeline único** de risco de qualidade na captação→ETA, alimentando o PSA operacional, sem misturar com CCO de distribuição.

## 3. Camadas de evento (ordem)

1. **CMA** — sensor/boia FQ + espectral (near real-time)  
2. **IAguas** — forecast / anomaly score (horizonte até ~7 d)  
3. **Lab** — geosmina / 2-MIB em µg/L (confirmação)  
4. **PSA** — regime `normal | alerta | crítico` via `classificar_psa`  
5. **Ação humana** — Seas / Inea / Defesa Civil / ajuste ETA (sem genAI no laço)

Limiares já no código (demonstração):

- alerta: lab ≥ 0,02 µg/L **ou** bloom_proxy  
- crítico: lab ≥ 0,1 µg/L **ou** (bloom_proxy e lab medido > 0)

Tempo de viagem do pulso: \(t = L/u\) (advecção) — ver `tempo_viagem_s` / ADE.

## 4. Integração

- CMA permanece fonte de imagem/sensor; IAguas emite score/alerta  
- Poseidon agrega no timeline PSA (consumo **read-only** do feed)  
- Compartilhamento CMA→órgãos já previsto; Poseidon no mesmo barramento de eventos  
- SCADA ETA recebe só orientação humana do PSA

## 5. Critérios de sucesso

- Alerta IAguas no timeline antes do lab positivo (quando aplicável)  
- Rastreabilidade: cada decisão PSA cita camadas 1–3  
- Pós-tolueno: tempo de detecção/comunicação mensurável vs 2024

## 6. Unknowns (não inventar)

- API / export oficial IAguas e CMA (formato, latência)  
- Frequência atual de lab geosmina / 2-MIB  
- Donos do PSA em Guandu vs Imunana-Laranjal

## 7. Referências

- `10-iaguas-supera-crosswalk.md`  
- `src/poseidon/quality.py`  
- Notícias CMA / IAguas (cedae.com.br); gap analysis 2026-09-05
