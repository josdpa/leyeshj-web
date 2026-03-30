"""
╔══════════════════════════════════════════════════════════════════╗
║  LEYESHJ.COM — Capa 3: Repositorio de Datos                     ║
║  Única capa que toca la base de datos · Pinza fina              ║
║  Usa el vector busqueda_vector con pesos A/B/C/D del SQL fix     ║
╚══════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from typing import Optional
import psycopg2
import psycopg2.extras
from Capas.Capa1_config import get_config


# ══════════════════════════════════════════════════════
#  CONEXIÓN (pool simple — escalable a pgbouncer/asyncpg)
# ══════════════════════════════════════════════════════

def _get_conn():
    """Conexión directa a Supabase PostgreSQL."""
    cfg = get_config()
    return psycopg2.connect(cfg.SUPABASE_DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)


# ══════════════════════════════════════════════════════
#  QUERY PRINCIPAL: Búsqueda Full-Text con ranking
#  Usa los pesos A/B/C/D del FIX_RANKING_PESOS.sql
# ══════════════════════════════════════════════════════

def buscar_articulos(
    q: str,
    codigo: Optional[str],
    pais: Optional[str],
    pagina: int,
    por_pagina: int,
) -> tuple[int, list[dict]]:
    """
    Retorna (total, lista_de_artículos).
    Ranking: sumilla/articulo_nro (peso A) > contenido (B) > titulo (C) > capitulo (D).
    """
    offset = (pagina - 1) * por_pagina
    tabla  = get_config().TABLA_LEYES

    # Filtros opcionales dinámicos — sin hardcoding
    filtros      = []
    params_count = []
    params_data  = []
    param_idx    = 1

    # Siempre hay query FTS
    filtros.append(
        f"busqueda_vector @@ websearch_to_tsquery('spanish', ${param_idx})"
    )
    params_count.append(q)
    params_data.append(q)
    param_idx += 1

    if codigo:
        filtros.append(f"UPPER(codigo) = UPPER(${param_idx})")
        params_count.append(codigo)
        params_data.append(codigo)
        param_idx += 1

    if pais:
        filtros.append(f"UPPER(pais) = UPPER(${param_idx})")
        params_count.append(pais)
        params_data.append(pais)
        param_idx += 1

    where = "WHERE " + " AND ".join(filtros)

    sql_count = f"SELECT COUNT(*) FROM {tabla} {where}"
    sql_data  = f"""
        SELECT
            id,
            codigo,
            articulo_nro,
            sumilla,
            titulo,
            capitulo,
            pais,
            ts_rank(busqueda_vector, websearch_to_tsquery('spanish', $1)) AS relevancia
        FROM {tabla}
        {where}
        ORDER BY relevancia DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    params_data += [por_pagina, offset]

    with _get_conn() as conn:
        with conn.cursor() as cur:
            # Psycopg2 usa %s, no $N — adaptamos
            sql_count_pg = sql_count.replace(f'$1', '%s').replace(f'$2', '%s').replace(f'$3', '%s')
            sql_data_pg  = _adaptar_params(sql_data, len(params_data))

            cur.execute(sql_count_pg, params_count)
            total = cur.fetchone()["count"]

            cur.execute(sql_data_pg, params_data)
            rows  = cur.fetchall()

    return int(total), [dict(r) for r in rows]


def obtener_articulo(articulo_id: int) -> Optional[dict]:
    """Retorna el artículo completo por ID, incluyendo contenido."""
    tabla = get_config().TABLA_LEYES
    sql   = f"""
        SELECT id, codigo, articulo_nro, sumilla, titulo, capitulo, contenido, pais
        FROM {tabla}
        WHERE id = %s
        LIMIT 1
    """
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (articulo_id,))
            row = cur.fetchone()
    return dict(row) if row else None


def listar_codigos() -> list[dict]:
    """
    Lista todos los cuerpos legales únicos con conteo de artículos.
    Universal — se auto-actualiza cuando cargas nuevos códigos.
    """
    tabla = get_config().TABLA_LEYES
    sql   = f"""
        SELECT
            codigo,
            MAX(titulo)       AS nombre,
            MAX(pais)         AS pais,
            COUNT(*)          AS articulos
        FROM {tabla}
        GROUP BY codigo
        ORDER BY codigo
    """
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def health_check_db() -> str:
    """Verifica conexión a la base de datos. Retorna 'ok' o el error."""
    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return "ok"
    except Exception as e:
        return f"error: {e}"


# ══════════════════════════════════════════════════════
#  UTILIDAD INTERNA
# ══════════════════════════════════════════════════════

def _adaptar_params(sql: str, n: int) -> str:
    """Convierte $1..$N a %s para psycopg2."""
    for i in range(n, 0, -1):
        sql = sql.replace(f'${i}', '%s')
    return sql
