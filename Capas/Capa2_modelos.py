"""
╔══════════════════════════════════════════════════════════════════╗
║  LEYESHJ.COM — Capa 2: Modelos de Datos (Pydantic)              ║
║  Contratos de entrada y salida · Sin hardcoding · Universal      ║
╚══════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════
#  MODELOS DE ENTRADA (Request)
# ══════════════════════════════════════════════════════

class BusquedaRequest(BaseModel):
    """Parámetros de búsqueda full-text sobre leyes_hj_global."""

    q: str = Field(..., min_length=2, max_length=300,
                   description="Término de búsqueda: 'pensión alimentos', 'tutela cautelar', etc.")
    codigo: Optional[str]  = Field(None,
                   description="Filtro por código legal. Ej: 'CC', 'CPP', 'CONST'")
    pais: Optional[str]    = Field(None,
                   description="Filtro por país: PE | CO | EC | BO")
    pagina: int            = Field(1, ge=1, description="Número de página (base 1)")
    por_pagina: int        = Field(20, ge=1, le=100)


class ExpedienteItemRequest(BaseModel):
    """Un artículo que el abogado agrega a su escrito."""
    articulo_id: int
    nota_abogado: Optional[str] = None   # comentario personalizado del abogado


# ══════════════════════════════════════════════════════
#  MODELOS DE SALIDA (Response)
# ══════════════════════════════════════════════════════

class ArticuloResumen(BaseModel):
    """Vista compacta — para listados y búsquedas."""
    id:            int
    codigo:        str
    articulo_nro:  Optional[str]
    sumilla:       Optional[str]
    titulo:        Optional[str]
    capitulo:      Optional[str]
    pais:          Optional[str]
    relevancia:    Optional[float] = None   # ts_rank del FTS


class ArticuloDetalle(ArticuloResumen):
    """Vista completa — cuando el abogado abre un artículo."""
    contenido:    Optional[str]
    cita_formal:  Optional[str] = None    # generada en Capa 4
    cita_apa:     Optional[str] = None    # generada en Capa 4


class BusquedaResponse(BaseModel):
    """Envelope estándar para respuestas de búsqueda."""
    total:     int
    pagina:    int
    paginas:   int
    resultados: list[ArticuloResumen]


class ArticuloDetalleResponse(BaseModel):
    ok:      bool = True
    articulo: ArticuloDetalle


class CodigoLegal(BaseModel):
    """Metadato de un cuerpo legal (para el grid de la home)."""
    codigo:      str
    nombre:      str
    descripcion: Optional[str]
    pais:        Optional[str]
    articulos:   int


class HealthResponse(BaseModel):
    status:  str
    version: str
    env:     str
    db:      str
