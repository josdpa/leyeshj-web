"""
╔══════════════════════════════════════════════════════════════════╗
║  LEYESHJ.COM — main.py (Punto de entrada FastAPI)               ║
║  Render.com: Start Command → uvicorn main:app --host 0.0.0.0   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Capas.Capa1_config import get_config
from Capas.Capa5_rutas  import router

cfg = get_config()

app = FastAPI(
    title       = cfg.APP_NOMBRE,
    version     = cfg.APP_VERSION,
    description = (
        "API backend de LeyesHJ — Motor de búsqueda legislativa para abogados "
        "de Perú, Colombia, Ecuador y Bolivia. "
        "Escalable para 120,000 usuarios concurrentes."
    ),
    docs_url    = "/docs",       # Swagger UI — desactivar en producción si se desea
    redoc_url   = "/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = cfg.CORS_ORIGINS + ["*"] if cfg.APP_ENV == "development" else cfg.CORS_ORIGINS,
    allow_credentials = True,
    allow_methods     = ["GET", "POST", "OPTIONS"],
    allow_headers     = ["*"],
)

# ── Rutas ─────────────────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")

# ── Raíz ──────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def raiz():
    return {
        "proyecto": "LeyesHJ API",
        "version":  cfg.APP_VERSION,
        "docs":     "/docs",
        "health":   "/api/v1/health",
    }
