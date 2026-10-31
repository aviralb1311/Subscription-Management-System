# Deployment Guide

## Backend (Render)
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Env: DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

## Frontend (Vercel)
- Build: `npm run build`
- Env: VITE_API_BASE_URL

## Database
- PostgreSQL managed
- Run: `alembic upgrade head`
