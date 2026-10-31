# Subscription Intelligence & Revenue Management Platform

Unified Subscription Intelligence & Revenue Management Platform built as a modular monolith.

## Tech Stack

**Frontend:** React, Vite, TypeScript, Tailwind CSS, Shadcn UI  
**Backend:** Python, FastAPI, SQLAlchemy, Alembic, Pydantic  
**Database:** PostgreSQL  
**Testing:** Pytest, Vitest  

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker and Docker Compose

### Setup

1. **Start PostgreSQL:**
```bash
docker-compose up -d
```

2. **Backend setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```

3. **Frontend setup:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Testing

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

## Project Status
Phase 1: Foundation and Scaffolding - Complete
