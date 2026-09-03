"""Outage Guandu 0.68/0.17/0.15, horizonte, PSA, envelope."""

from __future__ import annotations

import numpy as np
import pytest

from poseidon.climate import (
    LSTMAttentionNumpy,
    clamp_horizonte,
    evento_extremo_afluencia,
    prever_demanda,
    regime_pressao,
    regime_qualidade,
    serie_fixture_hidraulica,
)
from poseidon.domain import (
    SHARE_AGUAS_DO_RIO,
    SHARE_IGUA,
    SHARE_RIO_MAIS,
    alocar_guandu_50,
    envelope,
)
from poseidon.models import cenario_demanda, cenario_geosmina, cenario_guandu_50
from poseidon.quality import classificar_psa


def test_envelope_live_false():
    e = envelope({"ok": True})
    assert e["meta"]["live"] is False
    assert "data" in e


def test_outage_split_068_017_015():
    aloc = alocar_guandu_50(22_500)
    assert SHARE_AGUAS_DO_RIO == pytest.approx(0.68)
    assert SHARE_IGUA == pytest.approx(0.17)
    assert SHARE_RIO_MAIS == pytest.approx(0.15)
    s = aloc["shares"]
    assert s["aguas_do_rio"] + s["igua"] + s["rio_mais"] == pytest.approx(1.0)
    a = aloc["alocacao_l_s"]
    assert a["aguas_do_rio"] == pytest.approx(22_500 * 0.68)
    assert a["igua"] == pytest.approx(22_500 * 0.17)
    assert a["rio_mais"] == pytest.approx(22_500 * 0.15)
    assert sum(a.values()) == pytest.approx(22_500)


def test_cenario_guandu_50_envelope():
    out = cenario_guandu_50()
    assert out["meta"]["live"] is False
    assert out["data"]["remanescente_l_s"] == 22_500


def test_demanda_horizonte_clamp():
    assert clamp_horizonte(0) == 1
    assert clamp_horizonte(-5) == 1
    assert clamp_horizonte(24) == 24
    assert clamp_horizonte(48) == 48
    assert clamp_horizonte(100) == 48
    d0 = cenario_demanda(0)
    assert d0["data"]["horizonte_h"] == 1
    assert d0["data"]["clamp"] is True
    d48 = cenario_demanda(48)
    assert d48["data"]["horizonte_h"] == 48
    assert len(d48["data"]["demanda_m3_s"]) == 48
    d99 = cenario_demanda(99)
    assert d99["data"]["horizonte_h"] == 48
    assert d99["data"]["clamp"] is True
    assert d99["meta"]["live"] is False


def test_lstm_atencao_soma_um_e_numpy_sem_torch():
    x = serie_fixture_hidraulica(16)
    mdl = LSTMAttentionNumpy(seed=3)
    out = mdl.forward(x)
    assert out["alpha"].shape == (16,)
    assert out["alpha"].sum() == pytest.approx(1.0, rel=1e-6)
    assert out["h"].shape[1] == mdl.hidden_size
    prev = prever_demanda(12, serie=x, model=mdl)
    assert prev["backend"].startswith("numpy-lstm-attention")
    assert len(prev["demanda_m3_s"]) == 12


def test_gev_nao_e_seguro():
    rng = np.random.default_rng(0)
    # afluências sintéticas (m³/s)
    q = rng.gumbel(40, 3, 80)
    ev = evento_extremo_afluencia(q, periodo_anos=20)
    assert ev["nao_e_seguro"] is True
    assert ev["nivel_retorno_m3_s"] > ev["mu"]
    assert ev["sigma"] > 0


def test_hmm_regimes():
    lab = np.array([0.005] * 8 + [0.05] * 6 + [0.18] * 6)
    r = regime_qualidade(lab)
    assert r["dominante"] in {"normal", "alerta", "crítico"}
    assert set(r["regimes"]) == {"normal", "alerta", "crítico"}
    p = regime_pressao(np.array([0.2, 0.3, 5.0, 5.5, 14.0, 15.0]))
    assert len(p["labels"]) == 6


def test_geosmina_acopla_ade_psa():
    out = cenario_geosmina(lab_ug_l=0.12, bloom_proxy=False)
    assert out["meta"]["live"] is False
    assert out["data"]["sensor_online_ng_l"] is False
    assert out["data"]["psa_captação"] == "crítico"
    assert out["data"]["t_viagem_s"] > 0
    assert "∂C/∂t" in out["data"]["ade"]["equation"]


def test_psa_thresholds_via_classificar():
    assert classificar_psa(0.02, False) == "alerta"
    assert classificar_psa(0.1, False) == "crítico"
