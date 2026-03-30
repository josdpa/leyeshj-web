"""
╔══════════════════════════════════════════════════════════════════╗
║  LEYESHJ.COM — Capa 4: Servicios (Lógica de Negocio)           ║
║  Búsqueda · Citas legales · Armador de expediente               ║
║  Escalable para 120,000 abogados en Latinoamérica              ║
╚══════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
import math
from typing import Optional
from datetime import datetime

from Capas.Capa1_config import get_config
from Capas.Capa2_modelos import (
    ArticuloResumen, ArticuloDetalle,
    BusquedaResponse, CodigoLegal,
)
import Capas.Capa3_repositorio as repo


# ══════════════════════════════════════════════════════
#  SERVICIO DE BÚSQUEDA
# ══════════════════════════════════════════════════════

def servicio_buscar(
    q: str,
    codigo: Optional[str],
    pais: Optional[str],
    pagina: int,
    por_pagina: int,
) -> BusquedaResponse:
    """
    Orquesta la búsqueda full-text.
    Normaliza, llama al repositorio, mapea a modelos Pydantic.
    """
    cfg        = get_config()
    por_pagina = min(por_pagina, cfg.MAX_RESULTADOS)

    total, rows = repo.buscar_articulos(
        q=q, codigo=codigo, pais=pais,
        pagina=pagina, por_pagina=por_pagina,
    )

    resultados = [
        ArticuloResumen(
            id           = r["id"],
            codigo       = r["codigo"],
            articulo_nro = r.get("articulo_nro"),
            sumilla      = r.get("sumilla"),
            titulo       = r.get("titulo"),
            capitulo     = r.get("capitulo"),
            pais         = r.get("pais"),
            relevancia   = round(float(r["relevancia"]), 4) if r.get("relevancia") else None,
        )
        for r in rows
    ]

    paginas = max(1, math.ceil(total / por_pagina))

    return BusquedaResponse(
        total=total,
        pagina=pagina,
        paginas=paginas,
        resultados=resultados,
    )


# ══════════════════════════════════════════════════════
#  SERVICIO DE DETALLE DE ARTÍCULO
# ══════════════════════════════════════════════════════

def servicio_detalle(articulo_id: int) -> Optional[ArticuloDetalle]:
    """Obtiene artículo completo + genera citas legales automáticamente."""
    row = repo.obtener_articulo(articulo_id)
    if not row:
        return None

    cita_formal, cita_apa = _generar_citas(row)

    return ArticuloDetalle(
        id           = row["id"],
        codigo       = row["codigo"],
        articulo_nro = row.get("articulo_nro"),
        sumilla      = row.get("sumilla"),
        titulo       = row.get("titulo"),
        capitulo     = row.get("capitulo"),
        contenido    = row.get("contenido"),
        pais         = row.get("pais"),
        cita_formal  = cita_formal,
        cita_apa     = cita_apa,
    )


# ══════════════════════════════════════════════════════
#  SERVICIO DE CATÁLOGO DE CÓDIGOS
# ══════════════════════════════════════════════════════

def servicio_listar_codigos(pais: Optional[str] = None) -> list[CodigoLegal]:
    """Retorna todos los cuerpos legales disponibles en la BD."""
    rows = repo.listar_codigos()

    if pais:
        rows = [r for r in rows if (r.get("pais") or "").upper() == pais.upper()]

    return [
        CodigoLegal(
            codigo      = r["codigo"],
            nombre      = r.get("nombre") or r["codigo"],
            descripcion = None,       # puede enriquecerse con tabla metadatos
            pais        = r.get("pais"),
            articulos   = int(r["articulos"]),
        )
        for r in rows
    ]


# ══════════════════════════════════════════════════════
#  GENERADOR DE CITAS LEGALES  (lógica pura — sin BD)
# ══════════════════════════════════════════════════════

# Mapa de nombres completos por código — extensible sin tocar el repositorio
_NOMBRES_CODIGOS: dict[str, str] = {
    "CONST":   "Constitución Política del Perú",
    "CC":      "Código Civil",
    "CPC":     "Código Procesal Civil (TUO)",
    "CP":      "Código Penal",
    "CPP":     "Código Procesal Penal (D.Leg. 957)",
    "CPPA":    "Código Procesal Penal Anterior (D.Leg. 638)",
    "CEP":     "Código de Ejecución Penal",
    "CNA":     "Código de los Niños y Adolescentes",
    "CT":      "Código Tributario (TUO)",
    "CCOMER":  "Código de Comercio",
    "CCONS":   "Código Procesal Constitucional",
    "CPMP":    "Código Penal Militar Policial",
    "CRPA":    "Código de Responsabilidad Penal de Adolescentes",
    # Añade nuevos sin tocar la Capa 3 ni la Capa 5
}

# País → nombre para cita APA
_PAISES: dict[str, str] = {
    "PE": "Perú",
    "CO": "Colombia",
    "EC": "Ecuador",
    "BO": "Bolivia",
}


def _generar_citas(row: dict) -> tuple[str, str]:
    """
    Genera automáticamente la cita legal directa y el formato APA
    a partir de los metadatos del artículo.
    No requiere intervención manual del abogado.
    """
    codigo      = row.get("codigo", "")
    art_nro     = row.get("articulo_nro") or ""
    sumilla     = row.get("sumilla") or ""
    pais_cod    = (row.get("pais") or "PE").upper()
    año_actual  = datetime.now().year

    nombre_ley  = _NOMBRES_CODIGOS.get(codigo.upper(), codigo)
    nombre_pais = _PAISES.get(pais_cod, pais_cod)

    # ── Cita directa (estilo jurídico peruano) ────────────────────
    partes = [nombre_ley]
    if art_nro:
        partes.append(art_nro)
    if sumilla:
        partes.append(f"«{sumilla}»")

    cita_formal = ", ".join(partes) + f". {nombre_pais}."

    # ── Cita APA 7.ª edición (legislación) ───────────────────────
    # Formato: Nombre de la Ley [Código], Artículo N, País, Año.
    cita_apa = (
        f"{nombre_ley} [{codigo}], "
        f"{art_nro + ', ' if art_nro else ''}"
        f"{nombre_pais}, {año_actual}."
    )

    return cita_formal, cita_apa
