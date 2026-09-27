# API Reference Specification

Base Endpoint: `http://127.0.0.1:8000/api`

Interactive OpenAPI Docs: `http://127.0.0.1:8000/api/docs`

---

## 🔐 Auth Endpoints
- `POST /api/auth/register` — Register new user
- `POST /api/auth/login` — Authenticate user & return JWT token
- `GET /api/auth/me` — Return current authenticated user profile

---

## 🌐 Competitor Management Endpoints
- `GET /api/competitors` — List registered competitors (Query params: `search`, `status`, `skip`, `limit`)
- `POST /api/competitors` — Register new competitor (Triggers auto website investigation)
- `GET /api/competitors/{id}` — Get competitor details & discovered sources
- `PUT /api/competitors/{id}` — Update competitor settings / interval
- `DELETE /api/competitors/{id}` — Delete competitor
- `POST /api/competitors/{id}/analyze` — Trigger website analyzer investigation
- `POST /api/competitors/{id}/check-now` — Trigger immediate production monitoring check
- `POST /api/competitors/{id}/pause` — Pause competitor monitoring
- `POST /api/competitors/{id}/resume` — Resume competitor monitoring

---

## 📰 Article Endpoints
- `GET /api/articles` — List detected articles (Query params: `competitor_id`, `search`, `method`, `within_target`, `skip`, `limit`)
- `GET /api/articles/{id}` — Get detailed article metadata, body preview, images, and detection timeline

---

## 📊 Monitoring Logs & Analytics Endpoints
- `GET /api/monitoring/checks` — List monitoring check execution logs
- `GET /api/monitoring/sources` — List discovered monitoring sources
- `GET /api/monitoring/notifications` — List generated dashboard notifications
- `GET /api/analytics/overview` — Get system health KPIs & average delay math
- `GET /api/analytics/detection-delays` — Return detection delay time-series chart data
- `GET /api/analytics/methods` — Return breakdown of detection methods & volume

---

## 🚀 100-Website Scale Engine Endpoints
- `POST /api/scale-test/seed` — Seed 100 realistic mock competitors
- `POST /api/scale-test/start` — Launch async scale worker loop
- `POST /api/scale-test/stop` — Pause scale worker loop
- `POST /api/scale-test/clear` — Purge scale test data
- `GET /api/scale-test/status` — Get live scale throughput metrics

---

## 🧪 Controlled Demo Website & Evidence Endpoints
- `GET /api/demo-site` — HTML blog homepage of controlled demo site
- `GET /api/demo-site/rss.xml` — RSS feed of controlled demo site
- `GET /api/demo-site/sitemap.xml` — XML sitemap of controlled demo site
- `POST /api/demo-site/publish` — Publish test article to demo blog
- `GET /api/evidence/verification` — Return academic compliance verification matrix

---

## ⚡ Real-Time Events Stream
- `GET /api/events/sse` — Server-Sent Events (SSE) streaming endpoint
