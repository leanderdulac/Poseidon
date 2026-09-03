"""API FastAPI do CCO Poseidon — demo sem JWT, bind 127.0.0.1.

Consultivo apenas. Sem escrita SCADA. Sem LLM no laço.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from poseidon import __version__
from poseidon.climate import clamp_horizonte
from poseidon.domain import INCIDENTES_FIXTURE, SISTEMAS, envelope
from poseidon.hydraulics import headloss, joukowsky_delta_p_pa
from poseidon.models import cenario_demanda, cenario_geosmina, cenario_guandu_50, psa_atual

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(
    title="Poseidon",
    description=(
        "CCO hidráulico — dinâmica dos fluidos para produção de água CEDAE. "
        "Modelos consultivos. Dados de demonstração (meta.live=false)."
    ),
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class HammerBody(BaseModel):
    delta_v_m_s: float = Field(..., description="ΔV = V_inicial − V_final (m/s)")
    c_m_s: float | None = Field(None, description="Celeridade; padrão 1000 m/s (tubo rígido)")


class HeadlossBody(BaseModel):
    L: float = Field(..., description="Comprimento (m)")
    D: float = Field(..., description="Diâmetro interno (m)")
    Q: float = Field(..., description="Vazão (m³/s)")
    method: Literal["darcy", "hazen"] = "darcy"
    c: float = Field(120.0, description="C de Hazen–Williams (empírico)")


class GeosminaBody(BaseModel):
    lab_ug_l: float | None = 0.05
    bloom_proxy: bool = False
    amplitude_ug_l: float | None = None


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "servico": "poseidon",
        "versao": __version__,
        "modo": "demonstracao",
        "scada_write": False,
        "llm_no_laco": False,
    }


@app.get("/api/v1/systems")
def systems() -> dict:
    return envelope({"sistemas": SISTEMAS}, recurso="systems")


@app.get("/api/v1/psa")
def psa() -> dict:
    return psa_atual()


@app.get("/api/v1/incidents")
def incidents() -> dict:
    return envelope({"incidentes": INCIDENTES_FIXTURE}, recurso="incidents")


@app.post("/api/v1/demo/geosmina")
def demo_geosmina(body: GeosminaBody | None = None) -> dict:
    b = body or GeosminaBody()
    return cenario_geosmina(
        lab_ug_l=b.lab_ug_l,
        bloom_proxy=b.bloom_proxy,
        amplitude_ug_l=b.amplitude_ug_l,
    )


@app.post("/api/v1/demo/guandu-50")
def demo_guandu_50() -> dict:
    return cenario_guandu_50()


@app.get("/api/v1/demanda")
def demanda(horizonte_h: int = Query(24, description="Horizonte em horas; clamp [1, 48]")) -> dict:
    h = clamp_horizonte(horizonte_h)
    out = cenario_demanda(horizonte_h)
    # garantir clamp visível mesmo se o cliente mandar fora do intervalo
    out["data"]["horizonte_h"] = h
    out["data"]["horizonte_solicitado"] = int(horizonte_h)
    out["data"]["clamp"] = h != int(horizonte_h)
    return out


@app.post("/api/v1/hydraulics/hammer")
def hydraulics_hammer(body: HammerBody) -> dict:
    c = body.c_m_s if body.c_m_s is not None else 1000.0
    res = joukowsky_delta_p_pa(body.delta_v_m_s, c_m_s=c)
    return envelope(res, recurso="joukowsky")


@app.post("/api/v1/hydraulics/headloss")
def hydraulics_headloss(body: HeadlossBody) -> dict:
    res = headloss(body.L, body.D, body.Q, method=body.method, c=body.c)
    return envelope(res, recurso="headloss")


if FRONTEND_DIR.is_dir():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        @app.get("/")
        def cco_index() -> FileResponse:
            return FileResponse(index)

        app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


def main() -> None:
    import uvicorn

    uvicorn.run(
        "poseidon.api:app",
        host="127.0.0.1",
        port=8877,
        reload=False,
    )


if __name__ == "__main__":
    main()
