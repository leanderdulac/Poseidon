"""API tokenless — health, systems, PSA, hammer, headloss, demos."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


from poseidon.api import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["scada_write"] is False
    assert body["llm_no_laco"] is False


def test_systems_envelope():
    r = client.get("/api/v1/systems")
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["live"] is False
    nomes = {s["nome"] for s in body["data"]["sistemas"]}
    assert "ETA Guandu" in nomes
    assert "Sistema Imunana-Laranjal" in nomes
    guandu = next(s for s in body["data"]["sistemas"] if s["id"] == "eta-guandu")
    assert guandu["vazao_nominal_l_s"] == 45_000
    assert guandu["coords"]["lat"] == pytest.approx(-22.759)


def test_psa_e_incidents():
    r = client.get("/api/v1/psa")
    assert r.status_code == 200
    assert r.json()["data"]["sensor_online_ng_l"] is False
    r2 = client.get("/api/v1/incidents")
    assert r2.status_code == 200
    ids = {i["id"] for i in r2.json()["data"]["incidentes"]}
    assert "guandu-50-2026-07-21" in ids
    assert "cma-botafogo-2026-06-09" in ids


def test_demo_guandu_50():
    r = client.post("/api/v1/demo/guandu-50")
    assert r.status_code == 200
    a = r.json()["data"]["alocacao_l_s"]
    assert a["aguas_do_rio"] == 22_500 * 0.68
    assert a["igua"] == 22_500 * 0.17
    assert a["rio_mais"] == 22_500 * 0.15


def test_demo_geosmina():
    r = client.post("/api/v1/demo/geosmina", json={"lab_ug_l": 0.05, "bloom_proxy": False})
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["psa_captação"] == "alerta"
    assert d["sensor_online_ng_l"] is False


def test_demanda_clamp_api():
    r = client.get("/api/v1/demanda", params={"horizonte_h": 24})
    assert r.status_code == 200
    assert len(r.json()["data"]["demanda_m3_s"]) == 24
    r2 = client.get("/api/v1/demanda", params={"horizonte_h": 200})
    assert r2.json()["data"]["horizonte_h"] == 48
    assert r2.json()["data"]["clamp"] is True
    r3 = client.get("/api/v1/demanda", params={"horizonte_h": 0})
    assert r3.json()["data"]["horizonte_h"] == 1


def test_hammer():
    r = client.post("/api/v1/hydraulics/hammer", json={"delta_v_m_s": 1.0})
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["delta_p_pa"] > 0
    assert d["c_m_s"] == 1000.0
    r2 = client.post("/api/v1/hydraulics/hammer", json={"delta_v_m_s": -1.0, "c_m_s": 1000})
    assert r2.json()["data"]["delta_p_pa"] < 0


def test_headloss_darcy_hazen():
    payload = {"L": 1000, "D": 0.8, "Q": 0.4, "method": "darcy"}
    r = client.post("/api/v1/hydraulics/headloss", json=payload)
    assert r.status_code == 200
    assert r.json()["data"]["delta_h_m"] > 0
    payload["method"] = "hazen"
    r2 = client.post("/api/v1/hydraulics/headloss", json=payload)
    assert r2.status_code == 200
    assert r2.json()["data"]["empirical"] is True
