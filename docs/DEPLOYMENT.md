# Deployment & Infrastructure Guide

## 1. Docker Compose Deployment

The application includes a production-ready `docker-compose.yml` for single-command orchestration:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./competitor_spy.db
      - MAX_WORKERS=10
    volumes:
      - ./backend/competitor_spy.db:/app/competitor_spy.db

  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api
    depends_on:
      - backend
```

To run:
```bash
docker-compose up --build
```

---

## 2. Cloud Platform Deployment Options

### Render / Railway Deployment
- **Backend Service**: Deploy `./backend` as a Python Web Service. Set start command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Frontend Service**: Deploy `./frontend` as a Next.js Web Service on Render or Vercel. Set `NEXT_PUBLIC_API_URL` environment variable pointing to the backend API URL.

---

## 3. Environment Variables Reference (`.env.example`)

```env
PROJECT_NAME="Competitor Blog Spy & Real-Time Content Monitoring System"
SECRET_KEY="supersecretkey_change_in_production"
DATABASE_URL="sqlite:///./competitor_spy.db"

MAX_WORKERS=10
MAX_CONCURRENT_REQUESTS=20
REQUEST_TIMEOUT=15
DEFAULT_MONITOR_INTERVAL=60

SMTP_HOST=""
SMTP_PORT=587
SMTP_USERNAME=""
SMTP_PASSWORD=""
SMTP_FROM="alerts@competitorspy.local"

PLAYWRIGHT_ENABLED=false
```
