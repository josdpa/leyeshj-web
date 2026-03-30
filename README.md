# LeyesHJ — Backend API

Motor de búsqueda legislativa para abogados de Perú, Colombia, Ecuador y Bolivia.  
Escalable para 120,000 usuarios · FastAPI + Supabase PostgreSQL + Vercel.

---

## Estructura

```
leyeshj-backend/
├── main.py                  ← Punto de entrada FastAPI
├── vercel.json              ← Configuración de deploy en Vercel
├── requirements.txt
├── .env.example             ← Plantilla de variables (copia a .env)
└── Capas/
    ├── Capa1_config.py      → Variables de entorno
    ├── Capa2_modelos.py     → Modelos Pydantic (contratos)
    ├── Capa3_repositorio.py → Queries a Supabase/PostgreSQL
    ├── Capa4_servicios.py   → Lógica de negocio + citas legales
    └── Capa5_rutas.py       → Endpoints FastAPI
```

---

## Variables de entorno en Vercel

En Vercel → Settings → Environment Variables, agrega:

| Variable | Dónde encontrarla en Supabase |
|---|---|
| `SUPABASE_URL` | Project Settings → API → Project URL |
| `SUPABASE_KEY` | Project Settings → API → `service_role` secret |
| `SUPABASE_DB_URL` | Project Settings → Database → URI (Transaction pooler) |
| `APP_ENV` | Escribe: `production` |
| `SECRET_KEY` | Cualquier string largo aleatorio |

---

## Endpoints

| Endpoint | Descripción |
|---|---|
| `GET /api/v1/buscar?q=pensión alimentos` | Búsqueda full-text con ranking |
| `GET /api/v1/buscar?q=alimentos&codigo=CC` | Filtrado por código legal |
| `GET /api/v1/buscar?q=alimentos&pais=PE` | Filtrado por país |
| `GET /api/v1/articulo/{id}` | Detalle + cita formal + cita APA |
| `GET /api/v1/codigos` | Catálogo de cuerpos legales en BD |
| `GET /api/v1/health` | Estado del servidor y BD |
| `GET /docs` | Swagger UI interactivo |

---

## Deploy en Vercel (paso a paso)

1. Sube esta carpeta a GitHub (repo: `leyeshj-backend`)
2. Entra a [vercel.com](https://vercel.com) → Import Project → selecciona el repo
3. Framework Preset: **Other**
4. Agrega las variables de entorno (tabla de arriba)
5. Click en **Deploy**

Tu API estará en: `https://leyeshj-backend.vercel.app/docs`
