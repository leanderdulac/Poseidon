"""Benchmark CEDAE × PUB × Paris × Berlim — métodos, capacidade, matriz."""

from __future__ import annotations

from fastapi.testclient import TestClient

from poseidon.api import app
from poseidon.benchmarks import (
    GUANDU_CAPACITY_L_S,
    LossMethod,
    assert_comparable,
    capacity_l_s_guandu_vs_peers,
    load_matrix,
    poseidon_actions,
)

client = TestClient(app)


def test_methods_differ_not_comparable():
    ok, reason = assert_comparable(LossMethod.SINISA_PCT, LossMethod.ILI)
    assert ok is False
    assert "diferem" in reason or "≠" in reason

    ok2, _ = assert_comparable(LossMethod.SINISA_PCT, LossMethod.SINISA_PCT)
    assert ok2 is True

    ok3, reason3 = assert_comparable(
        "SINISA % distribuição",
        "Distribution Losses %",
    )
    assert ok3 is False
    assert "SINISA_PCT" in reason3 and "DIST_LOSS_PCT" in reason3


def test_guandu_capacity_gt_each_peer():
    cap = capacity_l_s_guandu_vs_peers()
    assert cap["guandu_capacity_l_s"] == GUANDU_CAPACITY_L_S == 45_000
    assert len(cap["peers"]) == 3
    for peer in cap["peers"]:
        assert GUANDU_CAPACITY_L_S > peer["l_s"], peer["label"]
        assert peer["guandu_gt"] is True
        if "sales_l_s" in peer:
            assert GUANDU_CAPACITY_L_S > peer["sales_l_s"]
            assert peer["guandu_gt_sales"] is True


def test_matrix_has_four_rows():
    matrix = load_matrix()
    rows = matrix["rows"]
    assert len(rows) == 4
    cities = {r["city"] for r in rows}
    assert any("CEDAE" in c or "Rio" in c for c in cities)
    assert any("Singapura" in c or "PUB" in c for c in cities)
    assert any("Paris" in c for c in cities)
    assert any("Berlim" in c or "Berlin" in c for c in cities)
    actions = poseidon_actions()
    assert len(actions) >= 1


def test_api_benchmarks_envelope():
    r = client.get("/api/v1/benchmarks")
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["live"] is False
    assert len(body["data"]["rows"]) == 4
    methods = {row["loss_method_enum"] for row in body["data"]["rows"]}
    assert LossMethod.SINISA_PCT.value in methods
    assert LossMethod.DIST_LOSS_PCT.value in methods
    assert LossMethod.SISPEA_P104.value in methods
    assert LossMethod.ILI.value in methods


def test_api_benchmarks_actions():
    r = client.get("/api/v1/benchmarks/actions")
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["live"] is False
    assert isinstance(body["data"]["actions"], list)
    assert len(body["data"]["actions"]) >= 1
