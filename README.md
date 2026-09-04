# Poseidon

**CCO hidráulico — dinâmica dos fluidos para produção de água CEDAE (Rio de Janeiro).**

Núcleo de comando **consultivo**. Sem escrita em SCADA. Sem LLM no laço de controle.
Toda telemetria deste repositório é **fixture** (`meta.live = false`). Não inventamos dados ao vivo.

> **Dados de demonstração.** Envelope `{data, meta}` com `meta.live=false` em todos os fixtures.

## O que é / o que não é

| É | Não é |
|---|---|
| Modelos de hidráulica e qualidade em SI | Sistema de despacho |
| Previsão 1–48 h de demanda/afluência (LSTM+atenção) | Calibração com telemetria real |
| PSA com laudo µg/L + proxy de ficocianina | Sensor on-line de geosmina em ng/L |
| Rateio Guandu 50 % como **fixture** | Contrato operacional das concessionárias |
| Código 100 % novo | Clone do ClimateWise |

A herança do ClimateWise é **matemática** (LSTM+atenção, GEV, HMM), reimplementada em numpy.
ClimateWise usava `x_t = [temp, precip, pressure, NAO, ENSO]`. Poseidon usa
`x_t = [Q_t, H_t, rain_t, temp_t, ENSO]`.

## Equações (SI)

### Continuidade / balanço de massa num nó

```
Σ Q_in = Σ Q_out + dV/dt
```

### Darcy–Weisbach

```
Δh = f (L/D) (V² / 2g)
V  = Q / (π D² / 4)
```

Fator `f`:

- laminar (`Re < 2300`): `f = 64 / Re`
- Swamee–Jain (explícito): `f = 0.25 / [log₁₀(ε/(3.7 D) + 5.74 / Re^0.9)]²`
- Colebrook–White (implícito): `1/√f = −2 log₁₀( ε/(3.7 D) + 2.51 /(Re √f) )`

### Hazen–Williams (empírico — rotulado como tal)

```
Q  = 0.2785 C D^{2.63} S^{0.54}
Δh = 10.67 L Q^{1.852} / (C^{1.852} D^{4.87})
```

Não deriva das equações de Navier–Stokes.

### Golpe de aríete de Joukowsky

```
Δp = ρ c ΔV
```

Convenção: `ΔV = V_inicial − V_final`. Parada súbita ⇒ `ΔV > 0` ⇒ sobrepressão `Δp > 0`.
Celeridade padrão **c = 1000 m/s** em tubo rígido (valor **documentado**, não medido).

### Saint-Venant 1D simplificado (adutora-tronco)

```
∂A/∂t + ∂Q/∂x = 0                         (continuidade)
S_f = S_0 ,  Q = α A^β                    (onda cinemática)
∂Q/∂t + g A ∂η/∂x + g A S_f = 0           (onda inercial, sem convecção)
```

### Advecção–dispersão (geosmina / 2-MIB surrogate)

```
∂C/∂t + u ∂C/∂x = D ∂²C/∂x² − k C
```

`C` em **µg/L** (laboratório). Proxy de florescimento = ficocianina. **Nunca** se afirma
sensor on-line em ng/L. O pulso na captação chega à entrega após o tempo de viagem `L/u`.

### LSTM + atenção (demanda 1–48 h)

```
h_t = LSTM(x_t, h_{t-1})
α_t = softmax( vᵀ tanh(W_h h_t + W_c c_t) )
ŷ   = Σ_t α_t · h_t
x_t = [Q_t, H_t, rain_t, temp_t, ENSO]
```

Implementação numpy (obrigatória). Torch é opcional e **não** é necessário para testes.
Pesos sintéticos (seed fixo) — modelo consultivo, não calibrado.

### GEV (eventos hidráulicos raros)

```
F(x) = exp{ −[1 + ξ(x−μ)/σ]^{−1/ξ} }
```

Uso: afluência extrema / rebentamento. **Não** é precificação de seguro.

### HMM de regime

Estados `{normal, alerta, crítico}` na qualidade da captação e em transientes de pressão
(Viterbi, emissões gaussianas).

## Fixtures de domínio (demonstração)

| Fixture | Valor |
|---|---|
| ETA Guandu | 45 000 L/s, ~80 % RM, coords −22.759, −43.451 |
| Imunana-Laranjal | 7 000 L/s |
| CMA Botafogo | 2026-06-09 |
| Novo Guandu (redundância) | março 2030 |
| Cenário 2026-07-21 18h | Guandu a 50 % → restam **22 500 L/s** |
| Rateio 50 % (fixture) | Águas do Rio **0.68** / Iguá **0.17** / Rio+ **0.15** |

PSA (demonstração):

- `lab ≥ 0.02 µg/L` **ou** proxy de bloom → **alerta**
- `lab ≥ 0.1 µg/L` **ou** (proxy **e** lab) → **crítico**

## Como correr

Python ≥ 3.11. Na pasta do projecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

API (apenas localhost):

```bash
uvicorn poseidon.api:app --host 127.0.0.1 --port 8877
```

- Saúde: http://127.0.0.1:8877/health
- CCO (UI): http://127.0.0.1:8877/
- OpenAPI: http://127.0.0.1:8877/docs

A UI é um CCO estático em português, servido pela própria API. Banner: **dados de demonstração**.

### Endpoints

| Método | Caminho | Notas |
|---|---|---|
| GET | `/health` | sem JWT |
| GET | `/api/v1/systems` | Guandu, Imunana-Laranjal |
| GET | `/api/v1/psa` | laudo + proxy |
| GET | `/api/v1/incidents` | CMA, Guandu 50 %, Novo Guandu |
| POST | `/api/v1/demo/geosmina` | pulso ADE + PSA |
| POST | `/api/v1/demo/guandu-50` | rateio 0.68/0.17/0.15 |
| GET | `/api/v1/demanda?horizonte_h=24` | clamp [1, 48] |
| POST | `/api/v1/hydraulics/hammer` | `{delta_v_m_s, c_m_s?}` |
| POST | `/api/v1/hydraulics/headloss` | `{L, D, Q, method=darcy\|hazen}` |

Bind: **127.0.0.1**. Demo **sem JWT**.


## Benchmark PUB / Paris / Berlim

Comparativo de referência (fixtures, `meta.live=false`) entre CEDAE/RJ, PUB Singapura,
Eau de Paris (+ SIAAP) e Berliner Wasserbetriebe.

- Brief: [`docs/benchmarks/09-comparativo-cedae-pub-paris-berlim.md`](docs/benchmarks/09-comparativo-cedae-pub-paris-berlim.md)
- Matriz: [`data/comparison/matrix.json`](data/comparison/matrix.json)
- Métricas por cidade: `data/{cedae,singapore,paris,berlin}/metrics.json`
- API: `GET /api/v1/benchmarks` · `GET /api/v1/benchmarks/actions`

**Aviso — métodos de perda não são intercambiáveis.** SINISA % (RJ), Distribution Losses %
(PUB), SISPEA P104.3 (Paris) e ILI (Berlim) vivem em campos distintos. Comparar direção e
ordem de grandeza; nunca plotar 0,87 % Berlim contra 50 % RJ na mesma barra sem converter
metodologia. Capacidade / vazão em L/s *é* comparável (Guandu 45 000 L/s vs peers).

## Layout

```
src/poseidon/    hidráulica, qualidade, clima, domínio, API
tests/           identidades, Joukowsky, ADE, PSA, outage, clamp
frontend/        CCO escuro em português (Leaflet)
docs/benchmarks/ brief comparativo PUB/Paris/Berlim
data/            matriz + métricas por cidade (fixtures)
```

## Licença

MIT. Código novo e independente. A inspiração matemática do ClimateWise (também MIT)
não implica cópia de ficheiros.
