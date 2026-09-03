"""Modelos climáticos/hidráulicos herdados matematicamente do ClimateWise.

Reimplementação independente (numpy; torch opcional se já estiver no venv).
Nenhum ficheiro do ClimateWise é copiado.

1. LSTM + atenção (horizonte curto 1–48 h)
   h_t = LSTM(x_t, h_{t-1})
   α_t = softmax( v^T tanh(W_h h_t + W_c c_t) )
   ŷ   = Σ_t α_t · h_t

   ClimateWise: x_t = [temp, precip, pressure, NAO, ENSO]
   Poseidon:    x_t = [Q_t, H_t, rain_t, temp_t, ENSO]
   Previsão: demanda de produção e afluência, 1–48 h.

2. GEV / valores extremos — eventos hidráulicos raros (rebentamento /
   afluência extrema). NÃO é precificação de seguro.

   F(x) = exp{ − [1 + ξ (x−μ)/σ ]^{−1/ξ} }   (ξ ≠ 0)
   F(x) = exp{ − exp( −(x−μ)/σ ) }            (ξ = 0, Gumbel)

3. HMM de regime: normal / alerta / crítico
   — qualidade da captação
   — transientes de pressão
   Viterbi com emissões gaussianas univariadas.

Pesos do LSTM de demonstração são sintéticos (seed fixo). Não calibrados
com telemetria real. meta.live=false.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

HORIZONTE_MIN_H = 1
HORIZONTE_MAX_H = 48
N_FEATURES = 5  # Q, H, rain, temp, ENSO
REGIMES = ("normal", "alerta", "crítico")

_TORCH_AVAILABLE = False
try:  # opcional — o fallback numpy DEVE funcionar sem torch
    import torch  # noqa: F401

    _TORCH_AVAILABLE = True
except Exception:
    _TORCH_AVAILABLE = False


def clamp_horizonte(horizonte_h: int | float) -> int:
    """Limita o horizonte de previsão a [1, 48] horas."""
    h = int(round(float(horizonte_h)))
    return max(HORIZONTE_MIN_H, min(HORIZONTE_MAX_H, h))


def _sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-z))


def _softmax(z: np.ndarray, axis: int = -1) -> np.ndarray:
    z = z - np.max(z, axis=axis, keepdims=True)
    e = np.exp(z)
    return e / np.sum(e, axis=axis, keepdims=True)


@dataclass
class LSTMAttentionNumpy:
    """LSTM de uma camada + atenção aditiva (Bahdanau), só numpy.

    Portas LSTM (todas as matrizes em R^{H×(H+F)} empilhadas por porta):
        i_t = σ(W_i x_t + U_i h_{t-1} + b_i)
        f_t = σ(W_f x_t + U_f h_{t-1} + b_f)
        o_t = σ(W_o x_t + U_o h_{t-1} + b_o)
        g_t = tanh(W_g x_t + U_g h_{t-1} + b_g)
        c_t = f_t ⊙ c_{t-1} + i_t ⊙ g_t
        h_t = o_t ⊙ tanh(c_t)

    Atenção:
        e_t = v^T tanh(W_h h_t + W_c c_t)
        α_t = softmax(e)_t
        ŷ   = Σ_t α_t h_t     (depois projeção linear para 2 saídas:
                               demanda, afluência)
    """

    input_size: int = N_FEATURES
    hidden_size: int = 8
    seed: int = 7

    def __post_init__(self) -> None:
        rng = np.random.default_rng(self.seed)
        H, F = self.hidden_size, self.input_size
        scale = 1.0 / np.sqrt(H + F)
        self.W_i = rng.normal(0, scale, (H, F))
        self.U_i = rng.normal(0, scale, (H, H))
        self.b_i = np.zeros(H)
        self.W_f = rng.normal(0, scale, (H, F))
        self.U_f = rng.normal(0, scale, (H, H))
        self.b_f = np.ones(H)  # forget bias ~ 1
        self.W_o = rng.normal(0, scale, (H, F))
        self.U_o = rng.normal(0, scale, (H, H))
        self.b_o = np.zeros(H)
        self.W_g = rng.normal(0, scale, (H, F))
        self.U_g = rng.normal(0, scale, (H, H))
        self.b_g = np.zeros(H)
        self.W_h = rng.normal(0, scale, (H, H))
        self.W_c = rng.normal(0, scale, (H, H))
        self.v = rng.normal(0, scale, H)
        # projeção ŷ → [demanda_rel, afluencia_rel]
        self.W_y = rng.normal(0, scale, (2, H))
        self.b_y = np.zeros(2)

    def lstm_step(
        self, x_t: np.ndarray, h_prev: np.ndarray, c_prev: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """h_t, c_t = LSTM(x_t, h_{t-1}, c_{t-1})."""
        i = _sigmoid(self.W_i @ x_t + self.U_i @ h_prev + self.b_i)
        f = _sigmoid(self.W_f @ x_t + self.U_f @ h_prev + self.b_f)
        o = _sigmoid(self.W_o @ x_t + self.U_o @ h_prev + self.b_o)
        g = np.tanh(self.W_g @ x_t + self.U_g @ h_prev + self.b_g)
        c_t = f * c_prev + i * g
        h_t = o * np.tanh(c_t)
        return h_t, c_t

    def forward(self, x: np.ndarray) -> dict:
        """x: (T, F). Devolve contexto ŷ, α, trajetórias h e c."""
        x = np.asarray(x, dtype=float)
        if x.ndim != 2 or x.shape[1] != self.input_size:
            raise ValueError(f"x deve ser (T, {self.input_size})")
        t_len = x.shape[0]
        H = self.hidden_size
        h = np.zeros((t_len, H))
        c = np.zeros((t_len, H))
        h_prev = np.zeros(H)
        c_prev = np.zeros(H)
        for t in range(t_len):
            h_prev, c_prev = self.lstm_step(x[t], h_prev, c_prev)
            h[t] = h_prev
            c[t] = c_prev
        # e_t = v^T tanh(W_h h_t + W_c c_t)
        e = np.einsum("h,th->t", self.v, np.tanh(h @ self.W_h.T + c @ self.W_c.T))
        alpha = _softmax(e, axis=0)
        context = alpha @ h  # (H,)   ŷ = Σ α_t h_t
        y = self.W_y @ context + self.b_y  # (2,)
        return {
            "h": h,
            "c": c,
            "alpha": alpha,
            "context": context,
            "y": y,
            "equation": "h_t=LSTM(x_t,h_{t-1}); α=softmax(v^T tanh(W_h h+W_c c)); ŷ=Σ α_t h_t",
        }


def serie_fixture_hidraulica(n: int = 48, seed: int = 11) -> np.ndarray:
    """Série de demonstração x_t = [Q, H, rain, temp, ENSO], meta.live=false.

    Q em m³/s (produção Guandu ~45 m³/s), H em m, rain mm/h, temp °C, ENSO índice.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    diurnal = 0.08 * np.sin(2 * np.pi * t / 24.0)
    q = 42.0 + 3.0 * diurnal + rng.normal(0, 0.4, n)  # m³/s
    head = 28.0 + 1.5 * np.sin(2 * np.pi * t / 24.0 + 0.4) + rng.normal(0, 0.2, n)
    rain = np.clip(rng.gamma(0.6, 1.2, n) - 0.4, 0, None)
    temp = 23.0 + 4.0 * np.sin(2 * np.pi * t / 24.0 - 0.5) + rng.normal(0, 0.3, n)
    enso = 0.4 + 0.05 * np.sin(2 * np.pi * t / 48.0) + rng.normal(0, 0.02, n)
    return np.column_stack([q, head, rain, temp, enso])


def prever_demanda(
    horizonte_h: int = 24,
    serie: np.ndarray | None = None,
    model: LSTMAttentionNumpy | None = None,
) -> dict:
    """Previsão consultiva 1–48 h de demanda de produção e afluência.

    Usa LSTM-atenção numpy. A amplitude absoluta ancora-se na última Q
    observada (persistência + correção de atenção) — pesos sintéticos.
    Horizonte é sempre clampado para [1, 48].
    """
    h = clamp_horizonte(horizonte_h)
    x = serie if serie is not None else serie_fixture_hidraulica(max(24, h))
    x = np.asarray(x, dtype=float)
    mdl = model or LSTMAttentionNumpy()
    out = mdl.forward(x)
    q_last = float(x[-1, 0])
    rain_mean = float(np.mean(x[:, 2]))
    # correção relativa limitada; ŷ[0] demanda, ŷ[1] afluência
    corr_dem = 0.04 * np.tanh(out["y"][0])
    corr_afl = 0.06 * np.tanh(out["y"][1]) + 0.01 * rain_mean
    t_fut = np.arange(1, h + 1)
    diurnal = 0.08 * np.sin(2 * np.pi * (len(x) + t_fut) / 24.0)
    demanda = q_last * (1.0 + corr_dem + diurnal)
    afluencia = q_last * (0.92 + corr_afl + 0.5 * diurnal)
    demanda = np.clip(demanda, 0.0, None)
    afluencia = np.clip(afluencia, 0.0, None)
    return {
        "horizonte_h": h,
        "horizonte_solicitado": int(horizonte_h),
        "clamp": h != int(horizonte_h) if not isinstance(horizonte_h, bool) else False,
        "demanda_m3_s": demanda.tolist(),
        "afluencia_m3_s": afluencia.tolist(),
        "alpha": out["alpha"].tolist(),
        "features": ["Q_t", "H_t", "rain_t", "temp_t", "ENSO"],
        "backend": "numpy-lstm-attention" + ("+torch-available" if _TORCH_AVAILABLE else ""),
        "equation": out["equation"],
        "advisory": True,
    }


# ---------------------------------------------------------------------------
# GEV — eventos hidráulicos raros (rebentamento / afluência extrema)
# ---------------------------------------------------------------------------

def gev_cdf(x: np.ndarray | float, mu: float, sigma: float, xi: float) -> np.ndarray:
    """F(x) = exp{ −[1 + ξ(x−μ)/σ]^{−1/ξ} }  (ξ≠0); Gumbel se ξ→0."""
    x = np.asarray(x, dtype=float)
    if sigma <= 0:
        raise ValueError("σ > 0")
    z = (x - mu) / sigma
    if abs(xi) < 1e-8:
        return np.exp(-np.exp(-z))
    t = 1.0 + xi * z
    out = np.full_like(t, np.nan, dtype=float)
    ok = t > 0
    out[ok] = np.exp(-(t[ok] ** (-1.0 / xi)))
    return out


def gev_return_level(period: float, mu: float, sigma: float, xi: float) -> float:
    """Nível de retorno x_p com p = 1/T: x_p = μ + σ/ξ [ (−ln(1−p))^{−ξ} − 1 ]."""
    if period <= 1:
        raise ValueError("período de retorno T > 1")
    p = 1.0 / period
    if abs(xi) < 1e-8:
        return float(mu - sigma * np.log(-np.log(1.0 - p)))
    return float(mu + sigma / xi * ((-np.log(1.0 - p)) ** (-xi) - 1.0))


def gev_fit_moments(amostra: np.ndarray) -> dict:
    """Ajuste GEV pelos L-moments simplificados (PWM de Hosking, 3 primeiros).

    Usado para afluência extrema / pressão de rebentamento — NÃO seguro.
    """
    x = np.sort(np.asarray(amostra, dtype=float).ravel())
    n = x.size
    if n < 10:
        raise ValueError("GEV requer n >= 10")
    # PWM b0, b1, b2
    b0 = float(np.mean(x))
    i = np.arange(1, n + 1)
    b1 = float(np.sum((i - 1) / (n - 1) * x) / n)
    b2 = float(np.sum(((i - 1) * (i - 2)) / ((n - 1) * (n - 2)) * x) / n)
    l1 = b0
    l2 = 2 * b1 - b0
    l3 = 6 * b2 - 6 * b1 + b0
    t3 = l3 / l2 if l2 != 0 else 0.0
    # aproximação de Hosking para ξ
    c = (2.0 / (3.0 + t3) - np.log(2) / np.log(3)) / (1.0 - np.log(2) / np.log(3))
    xi = float(7.859 * c + 2.9554 * c * c)
    # Γ(1+ξ) — Hosking; se ξ ≤ -1 o momento não existe, recua para Gumbel.
    if xi <= -0.99:
        xi = -0.99
    try:
        g1 = float(_gamma(1.0 + xi))
    except (ValueError, OverflowError):
        g1 = 1.0
    if abs(xi) < 1e-6:
        sigma = l2 / np.log(2)
        mu = l1 - 0.5772156649 * sigma
    else:
        sigma = l2 * xi / ((1.0 - 2.0 ** (-xi)) * g1)
        mu = l1 - sigma * (g1 - 1.0) / xi
    return {
        "mu": float(mu),
        "sigma": float(abs(sigma)),
        "xi": float(xi),
        "n": int(n),
        "uso": "afluencia_extrema_ou_rebentamento",
        "nao_e_seguro": True,
        "equation": "F(x)=exp{−[1+ξ(x−μ)/σ]^(−1/ξ)}",
    }


def _gamma(z: float) -> float:
    """Γ(z) via math.gamma."""
    import math

    return math.gamma(z)


def evento_extremo_afluencia(vazao_m3_s: np.ndarray, periodo_anos: float = 50.0) -> dict:
    """Nível de retorno GEV para afluência (demonstração)."""
    fit = gev_fit_moments(vazao_m3_s)
    nivel = gev_return_level(periodo_anos, fit["mu"], fit["sigma"], fit["xi"])
    return {**fit, "periodo_anos": float(periodo_anos), "nivel_retorno_m3_s": float(nivel)}


# ---------------------------------------------------------------------------
# HMM — regime normal / alerta / crítico
# ---------------------------------------------------------------------------

def hmm_viterbi(
    obs: np.ndarray,
    means: np.ndarray,
    stds: np.ndarray,
    log_start: np.ndarray | None = None,
    log_trans: np.ndarray | None = None,
) -> dict:
    """Viterbi gaussiano univariado, 3 estados: normal, alerta, crítico.

    Emissão:  p(x|s) = N(μ_s, σ_s²)
    Transição padrão: persistente na diagonal (regime hidráulico muda devagar).
    """
    x = np.asarray(obs, dtype=float).ravel()
    n = x.size
    k = 3
    means = np.asarray(means, dtype=float)
    stds = np.asarray(stds, dtype=float)
    if log_start is None:
        log_start = np.log(np.array([0.70, 0.20, 0.10]))
    if log_trans is None:
        trans = np.array(
            [
                [0.90, 0.08, 0.02],
                [0.10, 0.80, 0.10],
                [0.05, 0.15, 0.80],
            ]
        )
        log_trans = np.log(trans)

    def log_emit(s: int, val: float) -> float:
        z = (val - means[s]) / stds[s]
        return -0.5 * z * z - np.log(stds[s]) - 0.5 * np.log(2 * np.pi)

    dp = np.full((n, k), -np.inf)
    ptr = np.zeros((n, k), dtype=int)
    for s in range(k):
        dp[0, s] = log_start[s] + log_emit(s, x[0])
    for t in range(1, n):
        for s in range(k):
            scores = dp[t - 1] + log_trans[:, s]
            ptr[t, s] = int(np.argmax(scores))
            dp[t, s] = scores[ptr[t, s]] + log_emit(s, x[t])
    path = np.zeros(n, dtype=int)
    path[-1] = int(np.argmax(dp[-1]))
    for t in range(n - 1, 0, -1):
        path[t - 1] = ptr[t, path[t]]
    labels = [REGIMES[i] for i in path]
    return {
        "states": path.tolist(),
        "labels": labels,
        "loglik": float(np.max(dp[-1])),
        "regimes": list(REGIMES),
        "dominante": max(set(labels), key=labels.count),
    }


def regime_qualidade(lab_ug_l_series: np.ndarray) -> dict:
    """HMM sobre concentração laboratorial de geosmina (µg/L)."""
    means = np.array([0.005, 0.04, 0.15])
    stds = np.array([0.01, 0.02, 0.05])
    return hmm_viterbi(lab_ug_l_series, means, stds)


def regime_pressao(delta_p_m_series: np.ndarray) -> dict:
    """HMM sobre transientes de pressão (m.c.a. de desvio)."""
    means = np.array([0.5, 4.0, 12.0])
    stds = np.array([0.8, 2.0, 4.0])
    return hmm_viterbi(np.abs(delta_p_m_series), means, stds)
