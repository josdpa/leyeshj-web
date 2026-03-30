"""
╔══════════════════════════════════════════════════════════════════╗
║  LEYESHJ.COM — Capa 5: Rutas (Endpoints FastAPI)                ║
║  Interfaz pública del backend · CORS configurado                 ║
║  Consultas entrantes de 120,000 abogados latinoamericanos       ║
╚══════════════════════════════════════════════════════════════════╝
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from Capas.Capa2_modelos import (
    BusquedaResponse,
    ArticuloDetalleResponse,
    HealthResponse,
    CodigoLegal,
)
from Capas.Capa4_servicios import (
    servicio_buscar,
    servicio_detalle,
    servicio_listar_codigos,
)
import Capas.Capa3_repositorio as repo
from Capas.Capa1_config import get_config

router = APIRouter()


# ══════════════════════════════════════════════════════
#  GET /buscar
#  Búsqueda full-text con ranking por pesos A/B/C/D
# ══════════════════════════════════════════════════════

@router.get(
    "/buscar",
    response_model=BusquedaResponse,
    summary="Búsqueda full-text de artículos",
    description=(
        "Busca artículos legales usando PostgreSQL FTS con ranking ponderado. "
        "sumilla y articulo_nro (peso A) > contenido (B) > titulo (C) > capitulo (D)."
    ),
)
def buscar(
    q: str = Query(..., min_length=2, max_length=300,
                   description="Término de búsqueda. Ej: 'pensión alimentos'"),
    codigo: Optional[str] = Query(None,
                   description="Filtro: código legal. Ej: CC, CP, CONST"),
    pais: Optional[str]   = Query(None,
                   description="Filtro: país. Ej: PE, CO, EC, BO"),
    pagina: int            = Query(1, ge=1),
    por_pagina: int        = Query(20, ge=1, le=100),
):
    cfg = get_config()
    return servicio_buscar(
        q=q, codigo=codigo, pais=pais,
        pagina=pagina,
        por_pagina=min(por_pagina, cfg.MAX_RESULTADOS),
    )


# ══════════════════════════════════════════════════════
#  GET /articulo/{id}
#  Detalle completo + citas legales auto-generadas
# ══════════════════════════════════════════════════════

@router.get(
    "/articulo/{articulo_id}",
    response_model=ArticuloDetalleResponse,
    summary="Detalle de artículo con citas legales",
)
def detalle(articulo_id: int):
    articulo = servicio_detalle(articulo_id)
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado.")
    return ArticuloDetalleResponse(articulo=articulo)


# ══════════════════════════════════════════════════════
#  GET /codigos
#  Catálogo de cuerpos legales disponibles en la BD
# ══════════════════════════════════════════════════════

@router.get(
    "/codigos",
    response_model=list[CodigoLegal],
    summary="Catálogo de códigos legales",
    description="Lista todos los cuerpos legales cargados en la base de datos.",
)
def codigos(
    pais: Optional[str] = Query(None, description="Filtro por país: PE | CO | EC | BO"),
):
    return servicio_listar_codigos(pais=pais)


# ══════════════════════════════════════════════════════
#  GET /health
#  Monitoreo de estado del servidor y la base de datos
# ══════════════════════════════════════════════════════

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    include_in_schema=False,   # No visible en Swagger público
)
def health():
    cfg    = get_config()
    db_ok  = repo.health_check_db()
    return HealthResponse(
        status  = "ok" if db_ok == "ok" else "degraded",
        version = cfg.APP_VERSION,
        env     = cfg.APP_ENV,
        db      = db_ok,
    )
