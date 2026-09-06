"""ALF-like Guandu→entrega: DDP+PBS fixtures (advisory only)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from poseidon.alf import (
    SHARES,
    analyze_series,
    baseline_envelope,
    demo_anomaly_envelope,
    load_baseline,
    load_leak_scenario,
    shares_sum,
)
from poseidon.api import app

client = TestClient(app)


def test_shares_sum_one():
    assert shares_sum() == pytest.approx(1.0)
    assert SHARES["aguas_do_rio"] + SHARES["igua"] + SHARES["rio_mais"] == pytest.approx(1.0)


def test_baseline_length_and_no_false_positive():
    raw = load_baseline()
    series = raw["data"]["series"]
    assert len(series) == 24
    assert raw["data"]["n_hours"] == 24
    out = analyze_series(raw, scenario_id=raw["data"]["id"])
    assert out["n_hours"] == 24
    assert out["anomaly_detected"] is False
    assert out["ddp"]["anomaly"] is False
    assert out["pbs"]["anomaly"] is False
    assert out["events"] == []
    assert out["scada_write"] is False
    # z-scores dentro da tolerância (|z| < 3)
    assert max(abs(z) for z in out["ddp"]["z_q"]) < 3.0
    assert max(abs(z) for z in out["ddp"]["z_h"]) < 3.0


def test_leak_anomaly_detected():
    baseline = load_baseline()
    leak = load_leak_scenario()
    out = analyze_series(
        leak,
        scenario_id=leak["data"]["id"],
        ref_series=baseline["data"]["series"],
    )
    assert out["anomaly_detected"] is True
    assert out["ddp"]["anomaly"] is True
    assert out["pbs"]["anomaly"] is True
    assert out["events"]
    ev = out["events"][0]
    assert ev["scada_write"] is False
    assert ev["advisory"] is True
    assert ev["meta"]["live"] is False
    assert ev["approx_reach_id"]
    # horas do cenário sintético
    for h in (10, 11, 12, 13):
        assert h in out["ddp"]["flagged_hours"] or h in out["pbs"]["flagged_hours"]


def test_baseline_envelope_meta():
    env = baseline_envelope()
    assert env["meta"]["live"] is False
    assert env["meta"].get("scada_write") is False
    assert env["data"]["fixture"]["n_hours"] == 24
    assert len(env["data"]["fixture"]["series"]) == 24
    assert env["data"]["analysis"]["anomaly_detected"] is False
    assert env["data"]["analysis"]["shares_sum"] == pytest.approx(1.0)
    assert env["data"]["analysis"]["guandu_context_l_s"] == 45_000


def test_demo_anomaly_envelope_meta():
    env = demo_anomaly_envelope()
    assert env["meta"]["live"] is False
    assert env["meta"].get("scada_write") is False
    assert env["data"]["analysis"]["anomaly_detected"] is True
    assert env["data"]["analysis"]["advisory_only"] is True
    assert env["data"]["analysis"]["scada_write"] is False


def test_api_alf_baseline():
    r = client.get("/api/v1/alf/baseline")
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["live"] is False
    assert len(body["data"]["fixture"]["series"]) == 24
    assert body["data"]["analysis"]["anomaly_detected"] is False


def test_api_alf_demo_anomaly():
    r = client.post("/api/v1/alf/demo/anomaly")
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["live"] is False
    assert body["data"]["analysis"]["anomaly_detected"] is True
    assert body["data"]["analysis"]["events"]
    assert body["data"]["analysis"]["events"][0]["scada_write"] is False
