"""Fixtures de domínio CEDAE / concessionárias — apenas demonstração.

Envelope obrigatório: {data, meta} com meta.live=false para fixtures.
Nunca inventar telemetria ao vivo.
"""

from __future__ import annotations

from typing import Any

META_FIXTURE: dict[str, Any] = {
    "live": False,
    "fonte": "fixture",
    "rotulo": "dados de demonstração",
    "aviso": "Não é telemetria ao vivo. Sem escrita em SCADA.",
}


def envelope(data: Any, **extra: Any) -> dict[str, Any]:
    """Empacota payload no envelope {data, meta} com meta.live=false por omissão."""
    meta = dict(META_FIXTURE)
    meta.update(extra)
    if "live" not in extra:
        meta["live"] = False
    return {"data": data, "meta": meta}


# --- sistemas de produção ---------------------------------------------------

ETA_GUANDU = {
    "id": "eta-guandu",
    "nome": "ETA Guandu",
    "tipo": "estação_tratamento",
    "vazao_nominal_l_s": 45_000,
    "fracao_rm": 0.80,
    "coords": {"lat": -22.759, "lon": -43.451},
    "notas": "Cerca de 80 % da Região Metropolitana do Rio. Fixture de demonstração.",
}

IMUNANA_LARANJAL = {
    "id": "imunana-laranjal",
    "nome": "Sistema Imunana-Laranjal",
    "tipo": "sistema_produtor",
    "vazao_nominal_l_s": 7_000,
    "coords": {"lat": -22.72, "lon": -42.99},
    "notas": "Capacidade nominal de demonstração 7 000 L/s.",
}

SISTEMAS = [ETA_GUANDU, IMUNANA_LARANJAL]

# --- concessionárias (rateio Guandu 50 %) -----------------------------------
# Rateio documentado como FIXTURE, não contrato operacional.

SHARE_AGUAS_DO_RIO = 0.68
SHARE_IGUA = 0.17
SHARE_RIO_MAIS = 0.15

CONCESSIONARIAS = [
    {
        "id": "aguas-do-rio",
        "nome": "Águas do Rio",
        "share_guandu_fixture": SHARE_AGUAS_DO_RIO,
    },
    {
        "id": "igua",
        "nome": "Iguá",
        "share_guandu_fixture": SHARE_IGUA,
    },
    {
        "id": "rio-mais",
        "nome": "Rio+",
        "share_guandu_fixture": SHARE_RIO_MAIS,
    },
]

GUANDU_NOMINAL_L_S = 45_000
GUANDU_50_REMANESCENTE_L_S = 22_500  # 50 % de 45 000 L/s — fixture

CENARIO_GUANDU_50 = {
    "id": "guandu-50-2026-07-21",
    "titulo": "ETA Guandu a 50 % da capacidade",
    "quando": "2026-07-21T18:00:00-03:00",
    "fracao_capacidade": 0.50,
    "vazao_remanescente_l_s": GUANDU_50_REMANESCENTE_L_S,
    "rateio_fixture": {
        "aguas_do_rio": SHARE_AGUAS_DO_RIO,
        "igua": SHARE_IGUA,
        "rio_mais": SHARE_RIO_MAIS,
    },
    "nota": (
        "Rateio 0.68 / 0.17 / 0.15 é fixture de demonstração "
        "(Águas do Rio / Iguá / Rio+). Não é despacho real."
    ),
}

CMA_BOTAFOGO = {
    "id": "cma-botafogo-2026-06-09",
    "titulo": "CMA Botafogo",
    "quando": "2026-06-09",
    "tipo": "centro_manobra_abastecimento",
    "local": "Botafogo, Rio de Janeiro",
    "nota": "Fixture histórico de demonstração — sem telemetria.",
}

NOVO_GUANDU = {
    "id": "novo-guandu",
    "titulo": "Novo Guandu — redundância",
    "quando": "2030-03",
    "tipo": "obra_redundancia",
    "nota": "Redundância prevista para março de 2030 (fixture de planeamento).",
}

INCIDENTES_FIXTURE = [
    {
        **CENARIO_GUANDU_50,
        "severidade": "crítico",
        "sistema_id": "eta-guandu",
    },
    {
        **CMA_BOTAFOGO,
        "severidade": "alerta",
        "sistema_id": "cma-botafogo",
    },
    {
        **NOVO_GUANDU,
        "severidade": "normal",
        "sistema_id": "eta-guandu",
        "status": "planeado",
    },
]


def alocar_guandu_50(remanescente_l_s: float = GUANDU_50_REMANESCENTE_L_S) -> dict:
    """Aloca 22 500 L/s restantes do cenário Guandu 50 % pelas shares fixture.

    Águas do Rio 0.68 / Iguá 0.17 / Rio+ 0.15  (documentado como fixture).
    """
    shares = {
        "aguas_do_rio": SHARE_AGUAS_DO_RIO,
        "igua": SHARE_IGUA,
        "rio_mais": SHARE_RIO_MAIS,
    }
    soma = sum(shares.values())
    if abs(soma - 1.0) > 1e-12:
        raise ValueError(f"shares devem somar 1, obtido {soma}")
    aloc = {k: remanescente_l_s * v for k, v in shares.items()}
    return {
        "remanescente_l_s": remanescente_l_s,
        "shares": shares,
        "alocacao_l_s": aloc,
        "soma_shares": soma,
        "fixture": True,
        "cenario": CENARIO_GUANDU_50["id"],
    }
