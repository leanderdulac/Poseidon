"""Identidades hidráulicas, Joukowsky, Saint-Venant, Darcy/HW."""

from __future__ import annotations

import math

import numpy as np
import pytest

from poseidon.hydraulics import (
    C_JOUKOWSKY_RIGID_M_S,
    G_M_S2,
    RHO_WATER_KG_M3,
    area_circular_m2,
    continuity_residual,
    darcy_weisbach_headloss_m,
    friction_colebrook_white,
    friction_swamee_jain,
    hazen_williams_discharge_m3_s,
    hazen_williams_headloss_m,
    headloss,
    inertial_wave_step,
    joukowsky_delta_p_pa,
    kinematic_wave_route,
    reynolds,
    velocity_m_s,
)


def test_continuidade_identidade_fecha():
    q_in = [1.2, 0.8]
    q_out = [1.5]
    dvdt = 0.5  # 2.0 - 1.5
    assert continuity_residual(q_in, q_out, dvdt) == pytest.approx(0.0, abs=1e-12)


def test_continuidade_residual_detecta_desbalanco():
    r = continuity_residual([2.0], [1.0], 0.0)
    assert r == pytest.approx(1.0)


def test_area_e_velocidade_circular():
    d = 2.0
    a = area_circular_m2(d)
    assert a == pytest.approx(math.pi, rel=1e-12)
    q = math.pi  # V = 1 m/s
    assert velocity_m_s(q, d) == pytest.approx(1.0)


def test_darcy_weisbach_identidade_delta_h():
    L, D, Q = 1000.0, 1.0, 1.0
    res = darcy_weisbach_headloss_m(L, D, Q, method="swamee")
    v = velocity_m_s(Q, D)
    esperado = res["f"] * (L / D) * (v * v) / (2.0 * G_M_S2)
    assert res["delta_h_m"] == pytest.approx(esperado, rel=1e-12)
    assert res["delta_h_m"] > 0


def test_darcy_colebrook_proximo_swamee():
    L, D, Q = 2000.0, 0.8, 0.5
    a = darcy_weisbach_headloss_m(L, D, Q, method="swamee")
    b = darcy_weisbach_headloss_m(L, D, Q, method="colebrook")
    # Swamee–Jain é aproximação de Colebrook: diferença relativa < 3 %
    assert abs(a["f"] - b["f"]) / b["f"] < 0.03
    assert a["re"] > 2300


def test_laminar_f_64_re():
    D = 0.05
    # Q pequeno ⇒ Re < 2300
    Q = 1e-5
    re = reynolds(Q, D)
    assert re < 2300
    f = friction_swamee_jain(re, D)
    assert f == pytest.approx(64.0 / re, rel=1e-12)
    assert friction_colebrook_white(re, D) == pytest.approx(64.0 / re)


def test_hazen_williams_empirico_positivo():
    L, D, Q = 1000.0, 0.5, 0.2
    hw = hazen_williams_headloss_m(L, D, Q, c=120)
    assert hw["empirical"] is True
    assert hw["delta_h_m"] > 0
    # Q a partir de S deve ser da mesma ordem
    s = hw["delta_h_m"] / L
    q_back = hazen_williams_discharge_m3_s(120, D, s)
    assert q_back == pytest.approx(Q, rel=0.05)


def test_headloss_fachada_darcy_hazen():
    d = headloss(500, 0.6, 0.3, method="darcy")
    h = headloss(500, 0.6, 0.3, method="hazen")
    assert "delta_h_m" in d and "delta_h_m" in h
    assert d["delta_h_m"] > 0 and h["delta_h_m"] > 0


def test_joukowsky_sinal_parada_sobrepressao():
    """ΔV = V_inicial − V_final > 0 (parada) ⇒ Δp > 0."""
    v = 1.2
    r = joukowsky_delta_p_pa(delta_v_m_s=v)  # parada súbita
    assert r["delta_p_pa"] > 0
    assert r["delta_p_pa"] == pytest.approx(RHO_WATER_KG_M3 * C_JOUKOWSKY_RIGID_M_S * v)
    # aceleração (ΔV < 0) ⇒ depressão
    r2 = joukowsky_delta_p_pa(delta_v_m_s=-v)
    assert r2["delta_p_pa"] < 0
    assert r2["delta_p_pa"] == pytest.approx(-r["delta_p_pa"])


def test_joukowsky_c_padrao_1000():
    r = joukowsky_delta_p_pa(1.0)
    assert r["c_m_s"] == 1000.0


def test_onda_cinematica_cfl_e_massa():
    q_up = np.ones(40) * 2.0
    q_up[:5] = 1.0  # degrau
    dx, dt, ck = 100.0, 10.0, 5.0  # Co = 0.5
    q = kinematic_wave_route(q_up, dx, dt, ck, q_init_m3_s=1.0)
    assert q.shape[0] == 40
    # no fim, a última célula deve aproximar o valor a montante
    assert q[-1, -1] == pytest.approx(2.0, rel=0.15)
    with pytest.raises(ValueError, match="CFL"):
        kinematic_wave_route(q_up, dx_m=10.0, dt_s=10.0, celerity_m_s=5.0)


def test_passo_inercial_nao_explode():
    n = 11
    q = np.ones(n) * 1.0
    eta = np.linspace(5.0, 4.0, n)
    a = np.ones(n) * 2.0
    q2, eta2 = inertial_wave_step(q, eta, a, dx_m=50.0, dt_s=0.5, sf=0.0001)
    assert np.all(np.isfinite(q2))
    assert np.all(np.isfinite(eta2))
    assert q2[0] == q[0] and q2[-1] == q[-1]
