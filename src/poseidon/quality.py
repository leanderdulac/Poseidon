"""Transporte de qualidade na adutora — ADE para geosmina / 2-MIB.

Equação de advecção–dispersão–reação (surrogates, NÃO sensor on-line ng/L):

    ∂C/∂t + u ∂C/∂x = D ∂²C/∂x² − k C

C em µg/L (laboratório). Proxy de florescimento = ficocianina (booleano/índice).
Nunca se afirma existência de sensor on-line de ng/L.

PSA (plano de segurança da água), limiares de demonstração:
    lab >= 0.02 µg/L  OU  proxy de bloom            → alerta
    lab >= 0.1  µg/L  OU  (proxy E lab presente)    → crítico

O pulso na captação chega à entrega após o tempo de viagem L/u (advecção).
"""

from __future__ import annotations

from typing import Literal

import numpy as np

LIMIAR_ALERTA_UG_L = 0.02
LIMIAR_CRITICO_UG_L = 0.1

RegimePSA = Literal["normal", "alerta", "crítico"]


def classificar_psa(
    lab_ug_l: float | None,
    bloom_proxy: bool = False,
) -> RegimePSA:
    """Classifica o PSA a partir de lab (µg/L) e proxy de ficocianina.

    Regras (documentadas, fixtures):
      - crítico se lab >= 0.1 µg/L  OU  (bloom_proxy e lab medido > 0)
      - alerta  se lab >= 0.02 µg/L OU bloom_proxy
      - normal  caso contrário

    lab=None significa ausência de laudo (não inventar ng/L on-line).
    """
    tem_lab = lab_ug_l is not None
    lab = float(lab_ug_l) if tem_lab else 0.0
    if (tem_lab and lab >= LIMIAR_CRITICO_UG_L) or (
        bloom_proxy and tem_lab and lab > 0.0
    ):
        return "crítico"
    if (tem_lab and lab >= LIMIAR_ALERTA_UG_L) or bloom_proxy:
        return "alerta"
    return "normal"


def tempo_viagem_s(length_m: float, u_m_s: float) -> float:
    """Tempo de viagem advectivo t = L / u (u > 0)."""
    if u_m_s <= 0:
        raise ValueError("u deve ser positivo para tempo de viagem")
    if length_m < 0:
        raise ValueError("L >= 0")
    return length_m / u_m_s


def ade_step(
    c: np.ndarray,
    u_m_s: float,
    d_m2_s: float,
    k_1_s: float,
    dx_m: float,
    dt_s: float,
    c_in_ug_l: float = 0.0,
) -> np.ndarray:
    """Um passo explícito da ADE 1D.

    Advecção upwind, dispersão centrada, reação de 1ª ordem:
        C_i^{n+1} = C_i^n
            − u Δt/Δx (C_i^n − C_{i-1}^n)          (u >= 0)
            + D Δt/Δx² (C_{i+1}^n − 2 C_i^n + C_{i-1}^n)
            − k Δt C_i^n

    Contorno a montante: C_0 = c_in (Dirichlet).
    Contorno a jusante: extrapolação zero-gradiente.
    CFL advectivo: u Δt/Δx ≤ 1; Fourier: D Δt/Δx² ≤ 1/2.
    """
    c = np.asarray(c, dtype=float)
    n = c.size
    if n < 3:
        raise ValueError("ADE requer >= 3 células")
    if dx_m <= 0 or dt_s <= 0:
        raise ValueError("dx, dt > 0")
    co = abs(u_m_s) * dt_s / dx_m
    fo = d_m2_s * dt_s / (dx_m * dx_m)
    if co > 1.0 + 1e-9:
        raise ValueError(f"CFL advectivo violado: Co={co:.3f} > 1")
    if fo > 0.5 + 1e-9:
        raise ValueError(f"Fourier violado: Fo={fo:.3f} > 1/2")

    c_new = c.copy()
    # interior
    for i in range(1, n - 1):
        if u_m_s >= 0:
            adv = u_m_s * (c[i] - c[i - 1]) / dx_m
        else:
            adv = u_m_s * (c[i + 1] - c[i]) / dx_m
        disp = d_m2_s * (c[i + 1] - 2.0 * c[i] + c[i - 1]) / (dx_m * dx_m)
        reac = k_1_s * c[i]
        c_new[i] = c[i] - dt_s * (adv - disp + reac)
    # montante Dirichlet
    c_new[0] = c_in_ug_l
    # jusante Neumann ~0
    c_new[-1] = c_new[-2]
    c_new[c_new < 0] = 0.0
    return c_new


def ade_integrate(
    c0: np.ndarray,
    u_m_s: float,
    d_m2_s: float,
    k_1_s: float,
    dx_m: float,
    dt_s: float,
    n_steps: int,
    c_in_series_ug_l: np.ndarray | float = 0.0,
) -> np.ndarray:
    """Integra a ADE n_steps. Retorna C(t, x) com forma (n_steps+1, n_x)."""
    c = np.asarray(c0, dtype=float).copy()
    hist = np.zeros((n_steps + 1, c.size), dtype=float)
    hist[0] = c
    cin = np.asarray(c_in_series_ug_l, dtype=float)
    for n in range(n_steps):
        c_in = float(cin[n]) if cin.ndim > 0 and cin.size > 1 else float(np.asarray(c_in_series_ug_l).reshape(-1)[0] if np.asarray(c_in_series_ug_l).size == 1 else (cin[min(n, cin.size - 1)] if cin.size else 0.0))
        if cin.ndim == 0:
            c_in = float(cin)
        elif cin.size == 1:
            c_in = float(cin[0])
        else:
            c_in = float(cin[min(n, cin.size - 1)])
        c = ade_step(c, u_m_s, d_m2_s, k_1_s, dx_m, dt_s, c_in_ug_l=c_in)
        hist[n + 1] = c
    return hist


def massa_total_ug(c_ug_l: np.ndarray, dx_m: float, area_m2: float) -> float:
    """Massa linear integrada: Σ C Δx A. C em µg/L = mg/m³; resultado em mg se A,Δx em m.

    µg/L ≡ mg/m³, portanto massa (mg) = Σ C_i * Δx * A.
    Usado para testar decaimento k>0 (massa cai) e conservação k=0,u=0.
    """
    return float(np.sum(c_ug_l) * dx_m * area_m2)


def pulso_geosmina(
    n_x: int,
    dx_m: float,
    u_m_s: float,
    d_m2_s: float,
    k_1_s: float,
    dt_s: float,
    amplitude_ug_l: float,
    duracao_s: float,
    t_final_s: float,
) -> dict:
    """Injeta um pulso de geosmina na captação e transporta até a entrega.

    Acoplamento PSA: a concentração na última célula (entrega) classifica
    o regime após o tempo de viagem L/u.
    """
    n_steps = int(round(t_final_s / dt_s))
    n_in = int(round(duracao_s / dt_s))
    cin = np.zeros(n_steps, dtype=float)
    cin[: max(n_in, 1)] = amplitude_ug_l
    c0 = np.zeros(n_x, dtype=float)
    hist = ade_integrate(c0, u_m_s, d_m2_s, k_1_s, dx_m, dt_s, n_steps, cin)
    length_m = (n_x - 1) * dx_m
    t_viagem = tempo_viagem_s(length_m, u_m_s) if u_m_s > 0 else float("inf")
    c_entrega = hist[:, -1]
    t = np.arange(n_steps + 1) * dt_s
    idx_chegada = int(min(n_steps, max(0, round(t_viagem / dt_s))))
    c_na_chegada = float(c_entrega[idx_chegada])
    c_pico_entrega = float(np.max(c_entrega))
    return {
        "hist": hist,
        "t_s": t,
        "c_entrega_ug_l": c_entrega,
        "t_viagem_s": float(t_viagem),
        "c_na_chegada_ug_l": c_na_chegada,
        "c_pico_entrega_ug_l": c_pico_entrega,
        "length_m": float(length_m),
        "equation": "∂C/∂t + u ∂C/∂x = D ∂²C/∂x² − k C",
    }
