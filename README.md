# Arbitraje Inteligente (Nivel A / Modo 1)

Monorepo con:
- `supabase_sql/`: SQL para crear tablas + RLS + trigger
- `backend/`: FastAPI (motor de oportunidades)
- `web/`: Next.js (dashboard)
- `extension/`: Extension Chrome (captura asistida)
- `mobile/`: Flutter (companion)

## Arranque rapido (local)
1) Ejecuta el SQL de `supabase_sql/schema.sql` en Supabase.
2) Backend:
   - Copia `backend/.env.example` a `backend/.env` y rellena valores
   - `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
3) Web:
   - Copia `web/.env.example` a `web/.env.local` y rellena valores
   - `cd web && npm i && npm run dev`
4) Abre `http://localhost:3000`

## Rutas web
- `/` login
- `/today` hoy (demo + refresh)
- `/opportunities` listado
- `/opportunity?id=...` detalle
- `/extension` copiar token y API Base
