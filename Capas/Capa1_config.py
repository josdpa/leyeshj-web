"""
╔══════════════════════════════════════════════════════════════════╗
║  LEYESHJ.COM — Capa 1: Configuración y Conexión                 ║
║  Arquitectura en Capas · Pinza Fina · Reloj Suizo               ║
║  Escalable: 120,000 abogados · Perú · Colombia · Ecuador · Bolivia ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Configuracion(BaseSettings):
    """
    Variables de entorno centralizadas.
    En Render.com → Environment Variables.
    En desarrollo  → archivo .env en la raíz.
    """

    # ── Supabase ──────────────────────────────────────────────────
    SUPABASE_URL: str
    SUPABASE_KEY: str                   # service_role key (backend privado)
    SUPABASE_DB_URL: str                # postgresql://... (direct connection)

    # ── App ───────────────────────────────────────────────────────
    APP_NOMBRE: str       = "LeyesHJ API"
    APP_VERSION: str      = "1.0.0"
    APP_ENV: str          = "production"   # development | production
    SECRET_KEY: str       = "cambia-esto-en-produccion"

    # ── CORS: dominios autorizados ────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "https://leyeshj.com",
        "https://www.leyeshj.com",
        "https://leyeshj-web.vercel.app",
        "https://leyeshj-web-kwm2.vercel.app",
        "https://leyeshj-web-uj9m.vercel.app",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # ── Paginación por defecto ────────────────────────────────────
    RESULTADOS_POR_PAGINA: int = 20
    MAX_RESULTADOS: int        = 100

    # ── Tabla principal en Supabase ───────────────────────────────
    TABLA_LEYES: str = "leyes_hj_global"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache(maxsize=1)
def get_config() -> Configuracion:
    """Singleton — se lee UNA sola vez al arrancar el servidor."""
    return Configuracion()
