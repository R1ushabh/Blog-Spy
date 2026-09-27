# Competitor Blog Spy & Real-Time Content Monitoring System

[![Academic Grade](https://img.shields.io/badge/Academic%20Grade-Production-emerald)](#)
[![Python](https://img.shields.io/badge/Backend-FastAPI%20%7C%20SQLAlchemy-3776AB)](#)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016%20%7C%20Tailwind-black)](#)
[![License](https://img.shields.io/badge/License-MIT-blue)](#)

An enterprise-grade, real-time competitor content intelligence and monitoring system designed for continuous article detection, exact delay measurement, canonical deduplication, multi-strategy website investigation, and 100-website load scalability.

---

## 🌟 Key Highlights & Academic Requirements Enforced

1. **Automatic Website Analyzer**: Investigates competitor domains, discovers RSS/Atom feeds, XML sitemap indexes, HTML article containers, JSON-LD schema, OpenGraph tags, and assigns strategy confidence scores.
2. **Multi-Strategy Detection Pipeline**: Combines RSS/Atom feed parsing, XML Sitemap & Sitemap Index discovery, and direct semantic HTML crawling.
3. **Continuous Background Monitoring**: Asynchronous worker queues and background scheduler repeatedly inspect registered targets without manual refresh.
4. **Exact Detection Delay Measurement**: Calculates `detection_delay = detected_at - publication_time` in exact seconds and human-formatted strings (`3 min 12 sec`, `38 sec`, `1 hr 02 min 08 sec`). Evaluates against the **5-minute primary performance target** (`✓ Within 5-min target` vs `⚠ Above target`).
5. **Canonical Deduplication Engine**: Enforces multi-tier fingerprinting using normalized canonical URLs, source URLs, SHA-256 content hashes, and database unique constraints.
6. **Failure Isolation & Health Recovery**: Isolated error handling prevents a slow or failing website from blocking the queue. Manages health transitions (`ONLINE` → `DEGRADED` → `OFFLINE`).
7. **100-Website Scale Engine**: Built-in scale engine with async workers, per-domain rate limiting, and real-time CPM throughput metrics.
8. **Controlled Demo Website (`/api/demo-site`)**: Built-in test blog publisher with dynamic RSS, Sitemap XML, and HTML article generation for end-to-end evaluation.
9. **Real-Time SSE Event Broadcasting**: Delivers instant dashboard notifications without page reloads using Server-Sent Events (SSE).
10. **Academic Audit & Evidence Matrix (`/evidence`)**: Interactive compliance verification page verifying all 15 academic requirements against live runtime state.

---

## 🏗 System Architecture Overview

```
                      ┌─────────────────────────────────┐
                      │          Next.js Web UI         │
                      │ (React, Tailwind, Recharts, SSE)│
                      └────────────────┬────────────────┘
                                       │
                                       ▼ REST API / SSE
                      ┌─────────────────────────────────┐
                      │           FastAPI API           │
                      └───────┬─────────────────┬───────┘
                              │                 │
                              ▼                 ▼
                      ┌───────────────┐ ┌───────────────┐
                      │  PostgreSQL / │ │  Async Worker │
                      │  SQLite DB    │ │  Scheduler    │
                      └───────────────┘ └───────┬───────┘
                                                │
                ┌───────────────────────────────┼───────────────────────────────┐
                ▼                               ▼                               ▼
     ┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
     │  RSS/Atom Detector  │         │  Sitemap Detector   │         │ Direct Page Crawler │
     └──────────┬──────────┘         └──────────┬──────────┘         └──────────┬──────────┘
                │                               │                               │
                └───────────────────────────────┼───────────────────────────────┘
                                                ▼
                                    ┌───────────────────────┐
                                    │ Content Extractor     │
                                    │ (Trafilatura/BS4)     │
                                    └───────────┬───────────┘
                                                ▼
                                    ┌───────────────────────┐
                                    │ Canonical Deduplicater│
                                    │ (SHA-256 + Canonical) │
                                    └───────────┬───────────┘
                                                ▼
                                    ┌───────────────────────┐
                                    │ Delay Calculator & DB │
                                    │ (Exact Seconds Math)  │
                                    └───────────┬───────────┘
                                                ▼
                                    ┌───────────────────────┐
                                    │ Real-Time SSE Alert   │
                                    └───────────────────────┘
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js v18+ & npm
- (Optional) Docker & Docker Compose

### Option A: Local Development Setup

#### 1. Backend Setup
```bash
# Navigate to backend and create virtual environment
cd backend
python -m venv venv

# Activate venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install email-validator

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
*Backend API will be running at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/api/docs`.*

#### 2. Frontend Setup
```bash
# Open a new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
*Frontend UI will be running at `http://localhost:3000`.*

---

### Option B: Docker Compose Setup

```bash
# Run full stack with single command
docker-compose up --build
```

---

## 🧪 Running Automated Tests

```bash
# Run pytest test suite verifying deduplication, delay math, and extraction
$env:PYTHONPATH="backend"
python -m pytest backend/tests
```

---

## 📄 Documentation Index

- [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Detailed System Design & Scalability Blueprint
- [`API.md`](docs/API.md) — Complete REST API & SSE Endpoints Reference
- [`DEPLOYMENT.md`](docs/DEPLOYMENT.md) — Production Deployment & Docker Guide
- [`DEMO_GUIDE.md`](docs/DEMO_GUIDE.md) — Step-by-Step Evaluator Demo Instructions
- [`PERFORMANCE.md`](docs/PERFORMANCE.md) — Strategy Benchmark & Delay Analysis Report
