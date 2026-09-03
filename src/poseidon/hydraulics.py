"""Hidráulica de adutoras e nós — unidades SI, modelos consultivos.

Equações implementadas (todas em SI: m, s, m³/s, Pa, kg/m³):

1. Continuidade / balanço de massa num nó
   Σ Q_in = Σ Q_out + dV/dt

2. Darcy–Weisbach
   Δh = f (L/D) (V² / 2g)
   V = Q / (π D² / 4)

   Fator de atrito f:
   - laminar (Re < 2300): f = 64 / Re
   - turbulento, Swamee–Jain (explícito):
     f = 0.25 / [log10(ε/(3.7 D) + 5.74 / Re^0.9)]²
   - turbulento, Colebrook–White (implícito, Newton):
     1/√f = -2 log10( ε/(3.7 D) + 2.51 / (Re √f) )

3. Hazen–Williams (empírico — NÃO é derivado de Navier–Stokes)
   Q = 0.2785 C D^{2.63} S^{0.54}
   Δh = 10.67 L Q^{1.852} / (C^{1.852} D^{4.87})
   com Q em m³/s, D e L em m, S = Δh/L (adimensional).

4. Golpe de aríete de Joukowsky
   Δp = ρ c ΔV
   Convenção: ΔV = V_inicial − V_final  (parada súbita ⇒ ΔV > 0 ⇒ Δp > 0).
   c ≈ 1000 m/s em tubo rígido (valor-padrão documentado; não medido).

5. Saint-Venant 1D simplificado num trecho de adutora
   Continuidade:  ∂A/∂t + ∂Q/∂x = 0
   Cinemática:    S_f = S_0,  Q = α A^β
   Inercial (sem convecção): ∂Q/∂t + g A ∂η/∂x + g A S_f = 0
"""

from __future__ import annotations

import math
from typing import Literal

import numpy as np

G_M_S2 = 9.80665
RHO_WATER_KG_M3 = 998.0
NU_WATER_M2_S = 1.0e-6  # 20 °C, cinemática
C_JOUKOWSKY_RIGID_M_S = 1000.0  # celeridade padrão em tubo rígido (documentada)
PI = math.pi


def continuity_residual(
    q_in_m3_s: np.ndarray | list[float],
    q_out_m3_s: np.ndarray | list[float],
    dV_dt_m3_s: float,
) -> float:
    """Resíduo da continuidade: Σ Q_in − Σ Q_out − dV/dt.

    Identidade: residual == 0 quando o balanço de massa fecha.
    Unidades: m³/s.
    """
    return float(np.sum(q_in_m3_s) - np.sum(q_out_m3_s) - dV_dt_m3_s)


def area_circular_m2(diameter_m: float) -> float:
    """Área da seção circular A = π D² / 4."""
    if diameter_m <= 0:
        raise ValueError("D deve ser positivo")
    return PI * diameter_m * diameter_m / 4.0


def velocity_m_s(q_m3_s: float, diameter_m: float) -> float:
    """V = Q / A, A = π D² / 4."""
    return q_m3_s / area_circular_m2(diameter_m)


def reynolds(q_m3_s: float, diameter_m: float, nu_m2_s: float = NU_WATER_M2_S) -> float:
    """Re = V D / ν."""
    v = velocity_m_s(q_m3_s, diameter_m)
    return abs(v) * diameter_m / nu_m2_s


def friction_swamee_jain(re: float, diameter_m: float, eps_m: float = 0.00015) -> float:
    """Fator de Darcy f pela fórmula explícita de Swamee–Jain.

    f = 0.25 / [log10(ε/(3.7 D) + 5.74 / Re^{0.9})]^2
    Para Re < 2300 usa-se f = 64/Re (laminar).
    """
    if re < 1e-12:
        return 0.0
    if re < 2300.0:
        return 64.0 / re
    arg = eps_m / (3.7 * diameter_m) + 5.74 / (re ** 0.9)
    if arg <= 0:
        raise ValueError("argumento inválido em Swamee–Jain")
    return 0.25 / (math.log10(arg) ** 2)


def friction_colebrook_white(
    re: float,
    diameter_m: float,
    eps_m: float = 0.00015,
    tol: float = 1e-10,
    max_iter: int = 50,
) -> float:
    """Fator de Darcy f pela equação implícita de Colebrook–White.

    1/√f = -2 log10( ε/(3.7 D) + 2.51 / (Re √f) )
    Chute inicial: Swamee–Jain. Newton em x = 1/√f.
    Laminar: f = 64/Re.
    """
    if re < 1e-12:
        return 0.0
    if re < 2300.0:
        return 64.0 / re
    f = friction_swamee_jain(re, diameter_m, eps_m)
    f = max(f, 1e-8)
    for _ in range(max_iter):
        sqrt_f = math.sqrt(f)
        inner = eps_m / (3.7 * diameter_m) + 2.51 / (re * sqrt_f)
        residual = 1.0 / sqrt_f + 2.0 * math.log10(inner)
        # d(1/√f)/df = -0.5 f^{-3/2}
        # d(2 log10(inner))/df = (2 / (inner ln 10)) * d(inner)/df
        d_inner_df = 2.51 / re * (-0.5) * f ** (-1.5)
        dres_df = -0.5 * f ** (-1.5) + (2.0 / (inner * math.log(10.0))) * d_inner_df
        if abs(dres_df) < 1e-18:
            break
        f_new = f - residual / dres_df
        if f_new <= 0:
            f_new = f * 0.5
        if abs(f_new - f) < tol:
            f = f_new
            break
        f = f_new
    return float(f)


def darcy_weisbach_headloss_m(
    length_m: float,
    diameter_m: float,
    q_m3_s: float,
    eps_m: float = 0.00015,
    method: Literal["swamee", "colebrook"] = "swamee",
) -> dict:
    """Perda de carga Darcy–Weisbach: Δh = f (L/D) (V² / 2g).

    Retorna Δh (m), f, V, Re. Vazão negativa inverte o sinal de Δh
    (perda no sentido do escoamento).
    """
    if length_m < 0 or diameter_m <= 0:
        raise ValueError("L >= 0 e D > 0")
    v = velocity_m_s(q_m3_s, diameter_m)
    re = reynolds(q_m3_s, diameter_m)
    if method == "colebrook":
        f = friction_colebrook_white(re, diameter_m, eps_m)
    else:
        f = friction_swamee_jain(re, diameter_m, eps_m)
    dh = f * (length_m / diameter_m) * (v * v) / (2.0 * G_M_S2)
    # sinal: perda a favor do escoamento
    if q_m3_s < 0:
        dh = -dh
    return {
        "delta_h_m": float(dh),
        "f": float(f),
        "v_m_s": float(v),
        "re": float(re),
        "method": method,
        "equation": "Δh = f (L/D) (V² / 2g)",
    }


def hazen_williams_discharge_m3_s(
    c: float,
    diameter_m: float,
    slope: float,
) -> float:
    """Vazão empírica de Hazen–Williams (SI).

    Q = 0.2785 C D^{2.63} S^{0.54}
    S = Δh/L (adimensional). Fórmula empírica, não derivada de NS.
    """
    if c <= 0 or diameter_m <= 0 or slope < 0:
        raise ValueError("C > 0, D > 0, S >= 0")
    return 0.2785 * c * (diameter_m ** 2.63) * (slope ** 0.54)


def hazen_williams_headloss_m(
    length_m: float,
    diameter_m: float,
    q_m3_s: float,
    c: float = 120.0,
) -> dict:
    """Perda de carga empírica de Hazen–Williams (SI).

    Δh = 10.67 L |Q|^{1.852} / (C^{1.852} D^{4.87})
    Sinal segue o da vazão. Empírico — rotulado como tal.
    """
    if length_m < 0 or diameter_m <= 0 or c <= 0:
        raise ValueError("L >= 0, D > 0, C > 0")
    mag = 10.67 * length_m * (abs(q_m3_s) ** 1.852) / (
        (c ** 1.852) * (diameter_m ** 4.87)
    )
    dh = math.copysign(mag, q_m3_s) if q_m3_s != 0 else 0.0
    return {
        "delta_h_m": float(dh),
        "c": float(c),
        "empirical": True,
        "equation": "Δh = 10.67 L Q^1.852 / (C^1.852 D^4.87)  [Hazen–Williams empírico]",
    }


def joukowsky_delta_p_pa(
    delta_v_m_s: float,
    c_m_s: float = C_JOUKOWSKY_RIGID_M_S,
    rho_kg_m3: float = RHO_WATER_KG_M3,
) -> dict:
    """Golpe de aríete de Joukowsky: Δp = ρ c ΔV.

    Convenção de sinal (teste "Joukowsky sign"):
        ΔV = V_inicial − V_final.
        Parada súbita (V → 0) ⇒ ΔV > 0 ⇒ Δp > 0 (sobrepressão).
        Aceleração súbita ⇒ ΔV < 0 ⇒ Δp < 0 (depressão).

    c padrão = 1000 m/s (tubo rígido, valor documentado, não medido).
    Δh = Δp / (ρ g).
    """
    if c_m_s <= 0 or rho_kg_m3 <= 0:
        raise ValueError("c e ρ devem ser positivos")
    dp = rho_kg_m3 * c_m_s * delta_v_m_s
    dh = dp / (rho_kg_m3 * G_M_S2)
    return {
        "delta_p_pa": float(dp),
        "delta_h_m": float(dh),
        "c_m_s": float(c_m_s),
        "rho_kg_m3": float(rho_kg_m3),
        "delta_v_m_s": float(delta_v_m_s),
        "equation": "Δp = ρ c ΔV",
        "sign_convention": "ΔV = V_inicial − V_final; parada ⇒ Δp > 0",
        "c_default_note": "c=1000 m/s é o padrão documentado para tubo rígido",
    }


def manning_alpha_beta(n: float, width_m: float, s0: float) -> tuple[float, float]:
    """Coeficientes da curva Q = α A^β para canal retangular largo (R ≈ y).

    Manning: Q = (1/n) A R^{2/3} S_0^{1/2}.
    Com R ≈ A/width (retângulo largo): Q = (1/n) width^{-2/3} S_0^{1/2} A^{5/3}
    ⇒ α = (1/n) width^{-2/3} √S_0 ,  β = 5/3.
    """
    if n <= 0 or width_m <= 0 or s0 < 0:
        raise ValueError("n > 0, width > 0, S0 >= 0")
    alpha = (1.0 / n) * (width_m ** (-2.0 / 3.0)) * math.sqrt(max(s0, 0.0))
    beta = 5.0 / 3.0
    return alpha, beta


def kinematic_wave_route(
    q_upstream_m3_s: np.ndarray,
    dx_m: float,
    dt_s: float,
    celerity_m_s: float,
    q_init_m3_s: float | None = None,
) -> np.ndarray:
    """Onda cinemática 1D (Saint-Venant simplificado) num tronco.

    ∂Q/∂t + c_k ∂Q/∂x = 0,  c_k = dQ/dA (celeridade cinemática).
    Esquema upwind FTBS: Q_i^{n+1} = Q_i^n − Co (Q_i^n − Q_{i-1}^n),
    Co = c_k Δt / Δx  (CFL: Co ≤ 1).

    q_upstream_m3_s: série temporal da vazão a montante (contorno).
    Retorna Q(x, t) com forma (n_t, n_x) — n_x definido pelo CFL e
    comprimento implícito: aqui usamos n_x células e o hidrograma
    de saída na última célula.
    """
    q_up = np.asarray(q_upstream_m3_s, dtype=float)
    n_t = q_up.size
    if dx_m <= 0 or dt_s <= 0 or celerity_m_s < 0:
        raise ValueError("dx, dt > 0 e celeridade >= 0")
    co = celerity_m_s * dt_s / dx_m
    if co > 1.0 + 1e-9:
        raise ValueError(f"CFL violado: Co={co:.3f} > 1")
    # 8 células de trecho (adutora-tronco de demonstração)
    n_x = 8
    q = np.zeros((n_t, n_x), dtype=float)
    q0 = q_init_m3_s if q_init_m3_s is not None else float(q_up[0])
    q[0, :] = q0
    for n in range(n_t - 1):
        q[n + 1, 0] = q_up[n + 1]
        for i in range(1, n_x):
            q[n + 1, i] = q[n, i] - co * (q[n, i] - q[n, i - 1])
    return q


def inertial_wave_step(
    q_m3_s: np.ndarray,
    eta_m: np.ndarray,
    area_m2: np.ndarray,
    dx_m: float,
    dt_s: float,
    sf: np.ndarray | float,
    g: float = G_M_S2,
) -> tuple[np.ndarray, np.ndarray]:
    """Um passo inercial (Saint-Venant sem convecção) em malha 1D.

    Continuidade (células):  A_i^{n+1} = A_i^n − (Δt/Δx) (Q_{i+1/2} − Q_{i-1/2})
    Aproximação: usamos Q nos nós e η como superfície livre.
    Momento: Q^{n+1} = Q^n − Δt g A ∂η/∂x − Δt g A S_f

    Retorna (q_new, eta_new). Modelo consultivo, malha curta.
    """
    q = np.asarray(q_m3_s, dtype=float).copy()
    eta = np.asarray(eta_m, dtype=float).copy()
    a = np.asarray(area_m2, dtype=float)
    n = q.size
    if n < 3:
        raise ValueError("malha 1D requer >= 3 nós")
    sf_arr = np.broadcast_to(np.asarray(sf, dtype=float), q.shape)
    # momento interior
    q_new = q.copy()
    for i in range(1, n - 1):
        detadx = (eta[i + 1] - eta[i - 1]) / (2.0 * dx_m)
        q_new[i] = q[i] - dt_s * g * a[i] * detadx - dt_s * g * a[i] * sf_arr[i]
    q_new[0] = q[0]
    q_new[-1] = q[-1]
    # continuidade → variação de η (A ≈ width * η, width efetivo = A/η se η>0)
    eta_new = eta.copy()
    for i in range(1, n - 1):
        dqx = (q_new[i + 1] - q_new[i - 1]) / (2.0 * dx_m)
        # dA/dt = - dQ/dx ; dη/dt = (1/width) dA/dt, width ≈ a/max(η, ε)
        width = a[i] / max(abs(eta[i]), 0.1)
        eta_new[i] = eta[i] - dt_s * dqx / width
    return q_new, eta_new


def headloss(
    length_m: float,
    diameter_m: float,
    q_m3_s: float,
    method: Literal["darcy", "hazen"] = "darcy",
    **kwargs,
) -> dict:
    """Fachada de perda de carga: method=darcy|hazen."""
    if method == "hazen":
        c = float(kwargs.get("c", 120.0))
        return hazen_williams_headloss_m(length_m, diameter_m, q_m3_s, c=c)
    dw_method = kwargs.get("friction", "swamee")
    eps = float(kwargs.get("eps_m", 0.00015))
    return darcy_weisbach_headloss_m(
        length_m, diameter_m, q_m3_s, eps_m=eps, method=dw_method
    )
