"""ADE: decaimento de massa, PSA, tempo de viagem."""

from __future__ import annotations

import numpy as np
import pytest

from poseidon.quality import (
    LIMIAR_ALERTA_UG_L,
    LIMIAR_CRITICO_UG_L,
    ade_integrate,
    classificar_psa,
    massa_total_ug,
    pulso_geosmina,
    tempo_viagem_s,
)


def test_psa_normal():
    assert classificar_psa(0.001, bloom_proxy=False) == "normal"
    assert classificar_psa(None, bloom_proxy=False) == "normal"


def test_psa_alerta_lab_ou_proxy():
    assert classificar_psa(LIMIAR_ALERTA_UG_L, False) == "alerta"
    assert classificar_psa(0.05, False) == "alerta"
    assert classificar_psa(None, bloom_proxy=True) == "alerta"


def test_psa_critico_lab_ou_proxy_mais_lab():
    assert classificar_psa(LIMIAR_CRITICO_UG_L, False) == "crítico"
    assert classificar_psa(0.2, False) == "crítico"
    # proxy + lab (>0) → crítico
    assert classificar_psa(0.03, bloom_proxy=True) == "crítico"


def test_ade_massa_decaimento_reacao():
    """u=0, k>0, cin=0: massa cai ~ exp(-k t) no interior (Dirichlet na borda)."""
    n_x = 21
    dx = 10.0
    c0 = np.ones(n_x) * 1.0
    k = 0.01
    dt = 0.5
    n_steps = 40
    hist = ade_integrate(c0, u_m_s=0.0, d_m2_s=0.0, k_1_s=k, dx_m=dx, dt_s=dt, n_steps=n_steps, c_in_series_ug_l=1.0)
    m0 = massa_total_ug(hist[0, 1:-1], dx, area_m2=1.0)
    m1 = massa_total_ug(hist[-1, 1:-1], dx, area_m2=1.0)
    assert m1 < m0
    # decaimento de 1ª ordem: m(t)/m0 ≈ exp(-k t)
    t = n_steps * dt
    razao = m1 / m0
    assert razao == pytest.approx(np.exp(-k * t), rel=0.15)


def test_ade_massa_quase_conservada_k0_u0():
    n_x = 15
    dx = 5.0
    c0 = np.zeros(n_x)
    c0[5:8] = 2.0
    hist = ade_integrate(
        c0, u_m_s=0.0, d_m2_s=0.05, k_1_s=0.0, dx_m=dx, dt_s=0.2, n_steps=30, c_in_series_ug_l=0.0
    )
    m0 = massa_total_ug(hist[0], dx, 1.0)
    m1 = massa_total_ug(hist[-1], dx, 1.0)
    # dispersão com Dirichlet 0 nas bordas perde um pouco nas extremidades;
    # interior deve manter a maior parte
    assert m1 > 0.7 * m0


def test_tempo_viagem_e_pulso():
    L, u = 4000.0, 1.0
    assert tempo_viagem_s(L, u) == pytest.approx(4000.0)
    run = pulso_geosmina(
        n_x=21,
        dx_m=200.0,
        u_m_s=1.0,
        d_m2_s=1.0,
        k_1_s=0.0,
        dt_s=20.0,
        amplitude_ug_l=0.2,
        duracao_s=80.0,
        t_final_s=5000.0,
    )
    assert run["t_viagem_s"] == pytest.approx(4000.0, rel=0.05)
    # o pico na entrega deve aparecer depois do tempo de viagem
    idx = int(np.argmax(run["c_entrega_ug_l"]))
    t_pico = run["t_s"][idx]
    assert t_pico >= 0.6 * run["t_viagem_s"]
    assert run["c_pico_entrega_ug_l"] > 0
