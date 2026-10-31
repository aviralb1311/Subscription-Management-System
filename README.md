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

## GitHub Repository
[https://github.com/aviralb1311/Subscription-Management-System](https://github.com/aviralb1311/Subscription-Management-System)

## Clone Instructions
```bash
git clone https://github.com/aviralb1311/Subscription-Management-System.git
cd Subscription-Management-System
```

## Development Workflow
1. Pull latest changes: `git pull origin main`
2. Make changes and run tests
3. Commit completed logical units of work
4. Push to remote at least once every hour during active development

## Contributing
- Follow modular monolith architecture
- Write tests for new functionality
- Never commit secrets or .env files
- Use meaningful commit messages
- Run tests before committing
