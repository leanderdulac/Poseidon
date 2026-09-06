"""ALF-like Guandu→entrega: DDP + PBS (fixtures, advisory only).

Espelha o espírito do PUB Anomaly Leak Finder (digital twin hidráulico +
baseline estatístico) na adução/macromedição — sem DMA residencial,
sem write-back SCADA, sem LLM no laço, sem telemetria CEDAE inventada.

DDP — Demand/pressure baseline ~24 h: média/desvio (rolling + referência);
      z-score com piso de σ para evitar falso positivo.
PBS — Physics-based simulation: Darcy–Weisbach + continuidade no tronco
      1–2 trechos Guandu → nós de entrega (shares 0.68/0.17/0.15).
Event cluster — se DDP e/ou PBS flagarem, emite evento consultivo.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from poseidon.domain import (
    SHARE_AGUAS_DO_RIO,
    SHARE_IGUA,
    SHARE_RIO_MAIS,
    envelope,
)
from poseidon.hydraulics import continuity_residual, darcy_weisbach_headloss_m

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ALF_DATA_DIR = PROJECT_ROOT / "data" / "alf"
BASELINE_PATH = ALF_DATA_DIR / "baseline_24h.json"
LEAK_PATH = ALF_DATA_DIR / "leak_synthetic.json"

GUANDU_CONTEXT_L_S = 45_000
GUANDU_CONTEXT_M3_S = 45.0

SHARES = {
    "aguas_do_rio": SHARE_AGUAS_DO_RIO,
    "igua": SHARE_IGUA,
    "rio_mais": SHARE_RIO_MAIS,
}

# Limiares de demonstração (fixtures; não calibrados em campo)
DDP_Z_THRESHOLD = 3.0
DDP_ROLLING_WINDOW = 6
DDP_SIGMA_FLOOR_Q = 0.8  # m³/s — piso anti-falso-positivo
DDP_SIGMA_FLOOR_H = 0.8  # m
PBS_HEAD_RESIDUAL_M = 3.0
PBS_CONTINUITY_RESIDUAL_M3_S = 1.5  # ~3 % de 45 m³/s


def shares_sum() -> float:
    return float(sum(SHARES.values()))


def load_fixture(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"fixture ALF ausente: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_baseline() -> dict[str, Any]:
    return load_fixture(BASELINE_PATH)


def load_leak_scenario() -> dict[str, Any]:
    return load_fixture(LEAK_PATH)


def _series_arrays(series: list[dict[str, Any]]) -> dict[str, np.ndarray]:
    q = np.array([p["q_guandu_m3_s"] for p in series], dtype=float)
    h = np.array([p["h_guandu_m"] for p in series], dtype=float)
    h_del = np.array(
        [p.get("h_delivery_m", p["h_guandu_m"]) for p in series], dtype=float
    )
    q_del = np.array([p["q_delivery_total_m3_s"] for p in series], dtype=float)
    hours = np.array([p["hour"] for p in series], dtype=int)
    return {"q": q, "h": h, "h_delivery": h_del, "q_delivery": q_del, "hours": hours}


def _ref_stats(
    ref_series: list[dict[str, Any]] | None,
    series: list[dict[str, Any]],
) -> dict[str, float]:
    """Estatísticas de referência (baseline) para z-score DDP."""
    src = ref_series if ref_series is not None else series
    arr = _series_arrays(src)
    return {
        "q_mean": float(np.mean(arr["q"])),
        "q_std": max(float(np.std(arr["q"])), DDP_SIGMA_FLOOR_Q),
        "h_mean": float(np.mean(arr["h"])),
        "h_std": max(float(np.std(arr["h"])), DDP_SIGMA_FLOOR_H),
    }


def ddp_analyze(
    series: list[dict[str, Any]],
    *,
    ref_series: list[dict[str, Any]] | None = None,
    window: int = DDP_ROLLING_WINDOW,
    z_threshold: float = DDP_Z_THRESHOLD,
) -> dict[str, Any]:
    """Baseline ~24 h: z-score vs referência + rolling mean/std.

    Flag se |z_ref| >= limiar em Q ou H. Piso de σ evita falso positivo
    quando o desvio amostral da janela é quase nulo.
    """
    arr = _series_arrays(series)
    q, h = arr["q"], arr["h"]
    n = len(q)
    stats = _ref_stats(ref_series, series)
    z_q = (q - stats["q_mean"]) / stats["q_std"]
    z_h = (h - stats["h_mean"]) / stats["h_std"]

    # rolling (informativo + flag auxiliar com piso)
    roll_flags = np.zeros(n, dtype=bool)
    roll_details: list[dict[str, Any]] = []
    for i in range(n):
        start = max(0, i - window)
        hist_q = q[start:i] if i > start else q[0:1]
        hist_h = h[start:i] if i > start else h[0:1]
        mq, sq = float(np.mean(hist_q)), max(float(np.std(hist_q)), DDP_SIGMA_FLOOR_Q)
        mh, sh = float(np.mean(hist_h)), max(float(np.std(hist_h)), DDP_SIGMA_FLOOR_H)
        rzq = (float(q[i]) - mq) / sq
        rzh = (float(h[i]) - mh) / sh
        mature = i >= window
        rflag = bool(mature and (abs(rzq) >= z_threshold or abs(rzh) >= z_threshold))
        roll_flags[i] = rflag
        roll_details.append(
            {
                "hour": int(arr["hours"][i]),
                "z_q_roll": round(float(rzq), 4),
                "z_h_roll": round(float(rzh), 4),
                "flag_roll": rflag,
            }
        )

    ref_flags = (np.abs(z_q) >= z_threshold) | (np.abs(z_h) >= z_threshold)
    flags = ref_flags | roll_flags
    details: list[dict[str, Any]] = []
    for i in range(n):
        details.append(
            {
                "hour": int(arr["hours"][i]),
                "z_q": round(float(z_q[i]), 4),
                "z_h": round(float(z_h[i]), 4),
                "z_q_roll": roll_details[i]["z_q_roll"],
                "z_h_roll": roll_details[i]["z_h_roll"],
                "flag": bool(flags[i]),
            }
        )

    return {
        "method": "DDP",
        "window": window,
        "z_threshold": z_threshold,
        "sigma_floor_q_m3_s": DDP_SIGMA_FLOOR_Q,
        "sigma_floor_h_m": DDP_SIGMA_FLOOR_H,
        "ref_stats": {k: round(v, 6) for k, v in stats.items()},
        "n_flags": int(flags.sum()),
        "flagged_hours": [int(arr["hours"][i]) for i in range(n) if flags[i]],
        "z_q": [round(float(x), 4) for x in z_q],
        "z_h": [round(float(x), 4) for x in z_h],
        "points": details,
        "anomaly": bool(flags.any()),
    }


def _simulate_trunk_head(
    q_m3_s: float,
    h_upstream_m: float,
    reaches: list[dict[str, Any]],
) -> dict[str, Any]:
    """Propaga perda de carga Darcy–Weisbach ao longo dos trechos."""
    h = float(h_upstream_m)
    losses: list[dict[str, Any]] = []
    for r in reaches:
        dw = darcy_weisbach_headloss_m(
            length_m=float(r["length_m"]),
            diameter_m=float(r["diameter_m"]),
            q_m3_s=float(q_m3_s),
            eps_m=float(r.get("eps_m", 0.0003)),
            method="swamee",
        )
        h = h - float(dw["delta_h_m"])
        losses.append(
            {
                "reach_id": r["id"],
                "delta_h_m": round(float(dw["delta_h_m"]), 4),
                "v_m_s": round(float(dw["v_m_s"]), 4),
                "re": round(float(dw["re"]), 1),
                "h_downstream_m": round(h, 4),
            }
        )
    return {
        "h_delivery_sim_m": round(h, 4),
        "losses": losses,
        "reach_ids": [r["id"] for r in reaches],
    }


def pbs_analyze(
    series: list[dict[str, Any]],
    trunk: dict[str, Any],
    *,
    head_residual_m: float = PBS_HEAD_RESIDUAL_M,
    continuity_residual_m3_s: float = PBS_CONTINUITY_RESIDUAL_M3_S,
) -> dict[str, Any]:
    """PBS: compara Q/H observados com simulação física + continuidade.

    Residual de cabeça = H_entrega_obs − H_entrega_sim(Darcy–Weisbach).
    Residual de continuidade = Q_guandu − Q_entrega (dV/dt=0).
    Localização ≈ trecho a jusante quando a continuidade falha.
    """
    reaches = list(trunk.get("reaches") or [])
    if not reaches:
        raise ValueError("trunk.reaches vazio")

    points: list[dict[str, Any]] = []
    flags: list[bool] = []
    for p in series:
        q_up = float(p["q_guandu_m3_s"])
        h_up = float(p["h_guandu_m"])
        q_del = float(p["q_delivery_total_m3_s"])
        h_del_obs = float(p.get("h_delivery_m", h_up))
        sim = _simulate_trunk_head(q_up, h_up, reaches)
        cres = continuity_residual([q_up], [q_del], dV_dt_m3_s=0.0)
        h_res = float(h_del_obs - sim["h_delivery_sim_m"])
        headloss_total = sum(x["delta_h_m"] for x in sim["losses"])
        cont_flag = abs(cres) >= continuity_residual_m3_s
        head_flag = abs(h_res) >= head_residual_m
        flagged = bool(cont_flag or head_flag)
        if cont_flag:
            reach_id = reaches[-1]["id"]
        elif head_flag and sim["losses"]:
            reach_id = max(sim["losses"], key=lambda x: abs(x["delta_h_m"]))["reach_id"]
        else:
            reach_id = None
        points.append(
            {
                "hour": int(p["hour"]),
                "q_guandu_m3_s": round(q_up, 6),
                "q_delivery_total_m3_s": round(q_del, 6),
                "h_delivery_obs_m": round(h_del_obs, 4),
                "h_delivery_sim_m": sim["h_delivery_sim_m"],
                "continuity_residual_m3_s": round(float(cres), 6),
                "head_residual_m": round(h_res, 4),
                "headloss_total_m": round(float(headloss_total), 4),
                "flag": flagged,
                "reach_id": reach_id,
            }
        )
        flags.append(flagged)

    flagged_hours = [points[i]["hour"] for i, f in enumerate(flags) if f]
    reach_votes: dict[str, int] = {}
    for pt in points:
        if pt["flag"] and pt["reach_id"]:
            reach_votes[pt["reach_id"]] = reach_votes.get(pt["reach_id"], 0) + 1
    approx_reach = (
        max(reach_votes, key=reach_votes.get) if reach_votes else reaches[-1]["id"]
    )

    return {
        "method": "PBS",
        "equation": "Δh = f (L/D) (V² / 2g); Σ Q_in = Σ Q_out + dV/dt",
        "head_residual_threshold_m": head_residual_m,
        "continuity_residual_threshold_m3_s": continuity_residual_m3_s,
        "n_flags": int(sum(flags)),
        "flagged_hours": flagged_hours,
        "approx_reach_id": approx_reach,
        "points": points,
        "anomaly": bool(any(flags)),
        "shares": dict(SHARES),
        "shares_sum": shares_sum(),
    }


def _severity(ddp: dict[str, Any], pbs: dict[str, Any]) -> str:
    n = int(ddp.get("n_flags", 0)) + int(pbs.get("n_flags", 0))
    both = bool(ddp.get("anomaly")) and bool(pbs.get("anomaly"))
    if both and n >= 4:
        return "crítico"
    if ddp.get("anomaly") or pbs.get("anomaly"):
        return "alerta"
    return "normal"


def cluster_events(
    ddp: dict[str, Any],
    pbs: dict[str, Any],
    *,
    scenario_id: str,
) -> list[dict[str, Any]]:
    """Emite eventos consultivos se DDP e/ou PBS flagarem."""
    if not ddp.get("anomaly") and not pbs.get("anomaly"):
        return []
    hours = sorted(
        set(ddp.get("flagged_hours") or []) | set(pbs.get("flagged_hours") or [])
    )
    sev = _severity(ddp, pbs)
    sources = []
    if ddp.get("anomaly"):
        sources.append("DDP")
    if pbs.get("anomaly"):
        sources.append("PBS")
    return [
        {
            "id": f"alf-event-{scenario_id}",
            "tipo": "anomalia_aducao",
            "sources": sources,
            "severity": sev,
            "approx_reach_id": pbs.get("approx_reach_id"),
            "flagged_hours": hours,
            "advisory": True,
            "scada_write": False,
            "meta": {"live": False, "scada_write": False},
            "mensagem": (
                "Anomalia de vazão/pressão no tronco Guandu→entrega "
                f"(trecho≈{pbs.get('approx_reach_id')}). Apenas advisory."
            ),
        }
    ]


def analyze_series(
    fixture: dict[str, Any],
    *,
    scenario_id: str | None = None,
    ref_series: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Corre DDP+PBS sobre um fixture {data, meta}."""
    data = fixture["data"] if "data" in fixture else fixture
    series = data["series"]
    trunk = data["trunk"]
    sid = scenario_id or data.get("id", "alf")
    ddp = ddp_analyze(series, ref_series=ref_series)
    pbs = pbs_analyze(series, trunk)
    events = cluster_events(ddp, pbs, scenario_id=sid)
    return {
        "id": sid,
        "label": data.get("label", "demo"),
        "n_hours": len(series),
        "guandu_context_l_s": GUANDU_CONTEXT_L_S,
        "guandu_context_m3_s": GUANDU_CONTEXT_M3_S,
        "shares": dict(SHARES),
        "shares_sum": shares_sum(),
        "ddp": ddp,
        "pbs": pbs,
        "events": events,
        "anomaly_detected": bool(events),
        "scada_write": False,
        "advisory_only": True,
    }


def baseline_envelope() -> dict[str, Any]:
    """GET /api/v1/alf/baseline — série 24 h + análise DDP+PBS."""
    raw = load_baseline()
    analysis = analyze_series(raw, scenario_id=raw["data"]["id"])
    payload = {
        "fixture": {
            "id": raw["data"]["id"],
            "description": raw["data"].get("description"),
            "n_hours": raw["data"]["n_hours"],
            "series": raw["data"]["series"],
            "trunk": raw["data"]["trunk"],
        },
        "analysis": analysis,
    }
    return envelope(
        payload,
        recurso="alf_baseline",
        scada_write=False,
        guandu_context_l_s=GUANDU_CONTEXT_L_S,
    )


def demo_anomaly_envelope() -> dict[str, Any]:
    """POST /api/v1/alf/demo/anomaly — DDP+PBS no fixture de ruptura sintética."""
    baseline = load_baseline()
    raw = load_leak_scenario()
    analysis = analyze_series(
        raw,
        scenario_id=raw["data"]["id"],
        ref_series=baseline["data"]["series"],
    )
    payload = {
        "fixture": {
            "id": raw["data"]["id"],
            "description": raw["data"].get("description"),
            "scenario": raw["data"].get("scenario"),
            "n_hours": raw["data"]["n_hours"],
            "trunk": raw["data"]["trunk"],
        },
        "analysis": analysis,
    }
    return envelope(
        payload,
        recurso="alf_demo_anomaly",
        cenario="leak_synthetic",
        scada_write=False,
        guandu_context_l_s=GUANDU_CONTEXT_L_S,
    )
