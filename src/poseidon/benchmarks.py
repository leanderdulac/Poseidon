"""Benchmark CEDAE × PUB Singapura × Paris × Berlim.

Métodos de perda NÃO são intercambiáveis. Comparar direção / ordem de grandeza,
nunca ponto a ponto sem converter metodologia.

Fontes: data/comparison/matrix.json e data/{cedae,singapore,paris,berlin}/metrics.json.
Envelope sempre com meta.live=false (fixtures de referência, não telemetria).
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

from poseidon.domain import envelope

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
MATRIX_PATH = DATA_DIR / "comparison" / "matrix.json"

# Fixture documentado (ETA Guandu) — mesmo valor de domain.GUANDU_NOMINAL_L_S
GUANDU_CAPACITY_L_S = 45_000

# Valores L/s documentados na matriz / briefs (aproximações explícitas).
# PUB: vendas totais 2025 ≈ 21_209 L/s (SingStat; sales ≠ production).
# Paris: média potável 2025 ≈ 5_842 L/s (Eau de Paris).
# Berlim: capacidade 12_731.5 L/s; vendas ≈ 6_876 L/s (EMAS/GB 2025).
PEER_L_S_APPROX: dict[str, dict[str, Any]] = {
    "singapore": {
        "label": "PUB Singapura",
        "kind": "sales",
        "l_s": 21_209,
        "note": "vendas potável+NEWater 2025 (~1_832_444 m³/d); sales ≠ production",
    },
    "paris": {
        "label": "Paris / Eau de Paris",
        "kind": "production_avg",
        "l_s": 5_842,
        "note": "504_759 m³/d média potável 2025 ≈ 5_842 L/s",
    },
    "berlin": {
        "label": "Berlim / BWB",
        "kind": "capacity",
        "l_s": 12_731.5,
        "sales_l_s": 6_876,
        "note": "capacidade 1_100_000 m³/d; vendas ~217e6 m³/a ≈ 6_876 L/s",
    },
}


class LossMethod(str, Enum):
    """Métodos de perda — campos distintos; nunca misturar na mesma barra."""

    SINISA_PCT = "SINISA_PCT"
    SISPEA_P104 = "SISPEA_P104"
    ILI = "ILI"
    DIST_LOSS_PCT = "DIST_LOSS_PCT"
    UNKNOWN = "UNKNOWN"


def _classify_loss_method(text: str | None) -> LossMethod:
    if not text:
        return LossMethod.UNKNOWN
    t = text.upper()
    # Ordem importa: PUB cita "não ILI" no texto de Distribution Losses.
    if "SINISA" in t:
        return LossMethod.SINISA_PCT
    if "SISPEA" in t or "P104" in t:
        return LossMethod.SISPEA_P104
    if "DISTRIBUTION LOSS" in t or "DISTLOSS" in t.replace(" ", "").replace("_", ""):
        return LossMethod.DIST_LOSS_PCT
    if t.strip().startswith("ILI") or " ILI " in f" {t} " or t.startswith("ILI "):
        return LossMethod.ILI
    if "ILI" in t and "DISTRIBUTION" not in t:
        return LossMethod.ILI
    return LossMethod.UNKNOWN


def _to_method(value: LossMethod | str) -> LossMethod:
    if isinstance(value, LossMethod):
        return value
    try:
        return LossMethod(value)
    except ValueError:
        return _classify_loss_method(str(value))


def load_matrix() -> dict[str, Any]:
    """Carrega data/comparison/matrix.json. Levanta FileNotFoundError se ausente."""
    if not MATRIX_PATH.is_file():
        raise FileNotFoundError(f"matriz ausente: {MATRIX_PATH}")
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def load_city_metrics(city: str) -> dict[str, Any]:
    """Carrega data/<city>/metrics.json ou status unavailable (sem inventar números)."""
    path = DATA_DIR / city / "metrics.json"
    if not path.is_file():
        return {
            "city": city,
            "status": "unavailable",
            "reason": f"ficheiro em falta: {path}",
        }
    return {
        "city": city,
        "status": "ok",
        "metrics": json.loads(path.read_text(encoding="utf-8")),
    }


def assert_comparable(
    a: LossMethod | str,
    b: LossMethod | str,
) -> tuple[bool, str]:
    """True só se o método de perda for o mesmo.

    Retorna (comparável, razão). Métodos diferentes ⇒ False + razão explícita.
    """
    ma, mb = _to_method(a), _to_method(b)
    if ma == LossMethod.UNKNOWN or mb == LossMethod.UNKNOWN:
        return False, f"método desconhecido: {ma.value} vs {mb.value}"
    if ma != mb:
        return False, (
            f"métodos diferem: {ma.value} ≠ {mb.value} — "
            "não comparar ponto a ponto sem converter metodologia"
        )
    return True, f"mesmo método: {ma.value}"


def capacity_l_s_guandu_vs_peers() -> dict[str, Any]:
    """Guandu 45_000 L/s vs peers (aproximações documentadas na matriz).

    Capacidade / vazão em L/s É comparável entre cidades. Perdas % NÃO.
    """
    peers = []
    for key, info in PEER_L_S_APPROX.items():
        entry = {
            "id": key,
            "label": info["label"],
            "kind": info["kind"],
            "l_s": info["l_s"],
            "guandu_gt": GUANDU_CAPACITY_L_S > float(info["l_s"]),
            "note": info["note"],
        }
        if "sales_l_s" in info:
            entry["sales_l_s"] = info["sales_l_s"]
            entry["guandu_gt_sales"] = GUANDU_CAPACITY_L_S > float(info["sales_l_s"])
        peers.append(entry)

    return {
        "guandu_capacity_l_s": GUANDU_CAPACITY_L_S,
        "guandu_note": "ETA Guandu fixture domain — capacidade nominal de demonstração",
        "approximation_warning": (
            "Peers usam vendas ou capacidade média documentada na matriz; "
            "não são telemetria ao vivo nem produção bruta homóloga."
        ),
        "peers": peers,
        "spof_note": (
            "Guandu sozinho (45_000 L/s) supera PUB vendas (~21k), Paris (~5.8k) "
            "e Berlim capacidade (~12.7k) — outlier de SPOF até Novo Guandu 2030."
        ),
    }


def poseidon_actions() -> list[str]:
    """Acções recomendadas a partir da matriz JSON."""
    matrix = load_matrix()
    actions = matrix.get("poseidon_actions") or []
    return list(actions)


def matrix_rows_enriched() -> list[dict[str, Any]]:
    """Linhas da matriz com LossMethod normalizado."""
    matrix = load_matrix()
    rows = []
    for row in matrix.get("rows") or []:
        method_text = row.get("loss_method")
        rows.append(
            {
                **row,
                "loss_method_enum": _classify_loss_method(method_text).value,
            }
        )
    return rows


def benchmarks_payload() -> dict[str, Any]:
    """Payload completo para GET /api/v1/benchmarks (envelope aplicado na API)."""
    matrix = load_matrix()
    cities = {}
    for city in ("cedae", "singapore", "paris", "berlin"):
        cities[city] = load_city_metrics(city)
    return {
        "rule": matrix.get("rule"),
        "retrieved_at": matrix.get("retrieved_at"),
        "rows": matrix_rows_enriched(),
        "capacity_l_s": capacity_l_s_guandu_vs_peers(),
        "cities": cities,
        "docs": "docs/benchmarks/09-comparativo-cedae-pub-paris-berlim.md",
    }


def actions_payload() -> dict[str, Any]:
    return {
        "actions": poseidon_actions(),
        "docs": "docs/benchmarks/09-comparativo-cedae-pub-paris-berlim.md",
    }


def benchmarks_envelope() -> dict[str, Any]:
    return envelope(benchmarks_payload(), recurso="benchmarks")


def actions_envelope() -> dict[str, Any]:
    return envelope(actions_payload(), recurso="benchmarks_actions")
