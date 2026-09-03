"""Fachadas de cenário: geosmina, outage Guandu, demanda."""

from __future__ import annotations

from typing import Any

import numpy as np

from poseidon.climate import clamp_horizonte, prever_demanda, regime_qualidade
from poseidon.domain import alocar_guandu_50, envelope
from poseidon.quality import (
    LIMIAR_ALERTA_UG_L,
    LIMIAR_CRITICO_UG_L,
    classificar_psa,
    pulso_geosmina,
)


def cenario_geosmina(
    lab_ug_l: float | None = 0.05,
    bloom_proxy: bool = False,
    amplitude_ug_l: float | None = None,
    u_m_s: float = 0.8,
    length_m: float = 8_000.0,
    k_1_s: float = 1e-5,
    d_m2_s: float = 2.0,
) -> dict[str, Any]:
    """Pulso de geosmina na captação → ADE na adutora → PSA na entrega.

    lab em µg/L (laboratório). Proxy = ficocianina. Nunca sensor ng/L on-line.
    O pulso chega à entrega após t = L/u.
    """
    amp = float(amplitude_ug_l if amplitude_ug_l is not None else (lab_ug_l or 0.05))
    dx = 200.0
    n_x = max(8, int(round(length_m / dx)) + 1)
    dt = 50.0
    t_viagem = length_m / u_m_s
    t_final = t_viagem * 1.8 + 600.0
    run = pulso_geosmina(
        n_x=n_x,
        dx_m=dx,
        u_m_s=u_m_s,
        d_m2_s=d_m2_s,
        k_1_s=k_1_s,
        dt_s=dt,
        amplitude_ug_l=amp,
        duracao_s=600.0,
        t_final_s=t_final,
    )
    c_ent = run["c_pico_entrega_ug_l"]
    # PSA na entrega usa o pico transportado; lab de captação é o laudo.
    regime_entrega = classificar_psa(c_ent, bloom_proxy=bloom_proxy)
    regime_lab = classificar_psa(lab_ug_l, bloom_proxy=bloom_proxy)
    hmm = regime_qualidade(run["c_entrega_ug_l"])
    payload = {
        "lab_captação_ug_l": lab_ug_l,
        "bloom_proxy_ficocianina": bloom_proxy,
        "sensor_online_ng_l": False,
        "aviso_sensor": "Apenas laudo laboratorial µg/L + proxy de ficocianina. Sem sensor on-line ng/L.",
        "psa_captação": regime_lab,
        "psa_entrega": regime_entrega,
        "c_pico_entrega_ug_l": c_ent,
        "t_viagem_s": run["t_viagem_s"],
        "t_viagem_h": run["t_viagem_s"] / 3600.0,
        "limiares_ug_l": {"alerta": LIMIAR_ALERTA_UG_L, "crítico": LIMIAR_CRITICO_UG_L},
        "ade": {
            "equation": run["equation"],
            "u_m_s": u_m_s,
            "D_m2_s": d_m2_s,
            "k_1_s": k_1_s,
            "length_m": run["length_m"],
        },
        "hmm_entrega": {"dominante": hmm["dominante"], "regimes": hmm["regimes"]},
    }
    return envelope(payload, cenario="geosmina")


def cenario_guandu_50() -> dict[str, Any]:
    """ETA Guandu a 50 % — 22 500 L/s rateados 0.68 / 0.17 / 0.15."""
    aloc = alocar_guandu_50()
    return envelope(aloc, cenario="guandu-50-2026-07-21")


def cenario_demanda(horizonte_h: int = 24) -> dict[str, Any]:
    """Demanda 1–48 h via LSTM-atenção (numpy). Horizonte clampado."""
    h_req = horizonte_h
    h = clamp_horizonte(h_req)
    prev = prever_demanda(h)
    prev["horizonte_solicitado"] = int(h_req)
    prev["clamp"] = int(h) != int(h_req)
    return envelope(prev, cenario="demanda")


def psa_atual(
    lab_ug_l: float | None = 0.008,
    bloom_proxy: bool = False,
) -> dict[str, Any]:
    """Estado PSA de demonstração (laudo + proxy, sem sensor ng/L)."""
    regime = classificar_psa(lab_ug_l, bloom_proxy)
    payload = {
        "regime": regime,
        "lab_ug_l": lab_ug_l,
        "bloom_proxy_ficocianina": bloom_proxy,
        "sensor_online_ng_l": False,
        "limiares_ug_l": {"alerta": LIMIAR_ALERTA_UG_L, "crítico": LIMIAR_CRITICO_UG_L},
        "regra": "lab>=0.02 ou proxy → alerta; lab>=0.1 ou proxy+lab → crítico",
    }
    return envelope(payload, cenario="psa")
