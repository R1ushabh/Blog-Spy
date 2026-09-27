# System Architecture & Technical Design Document

## 1. System Overview
The **Competitor Blog Spy & Real-Time Content Monitoring System** is a decoupled, asynchronous observability platform engineered to monitor competitor publications across multiple content discovery vectors.

## 2. Decoupled Architecture Diagram

```
                ┌─────────────────────┐
                │      Web UI         │
                │    Next.js / React  │
                └──────────┬──────────┘
                           │ REST / SSE
                           ▼
                ┌─────────────────────┐
                │     FastAPI API     │
                └──────┬─────────┬────┘
                       │         │
                       ▼         ▼
                PostgreSQL     Redis
                                 │
                                 ▼
                       ┌─────────────────┐
                       │ Worker Scheduler│
                       └────────┬────────┘
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
          RSS Worker       Sitemap Worker     Direct Worker
              │                 │                  │
              └─────────────────┼──────────────────┘
                                ▼
                      Content Extraction
                                │
                                ▼
                         Deduplication
                                │
                                ▼
                         Article Storage
                                │
                                ▼
                         Notifications
```

## 3. Core Subsystems

### A. Automatic Website Analyzer (`app.services.analyzer`)
- **Inspection Logic**: Crawls target domain, follows HTTP redirects, parses `<link rel="alternate">` tags for RSS/Atom, inspects `/robots.txt` for sitemaps, checks standard endpoints (`/sitemap.xml`, `/rss.xml`), and evaluates schema.org JSON-LD / OpenGraph.
- **Output**: Returns discovered sources, strategy confidence ratings (High/Medium/Low), and a strategy selection rationale.

### B. Multi-Strategy Content Detectors
1. **RSS / Atom Detector (`app.services.rss_detector`)**: Parses RSS 2.0 & Atom feeds. Extracts date variants (`pubDate`, `dc:date`, `published`, `updated`).
2. **XML Sitemap Detector (`app.services.sitemap_detector`)**: Parses nested sitemaps and sitemap indexes recursively. Extracts article locations & `lastmod` timestamps.
3. **Direct Page Detector (`app.services.direct_detector`)**: Scans HTML blog index pages. Inspects `<article>` elements, subpath patterns (`/blog/`, `/news/`), and canonical dates.

### C. Article Content Extractor (`app.services.extractor`)
- Employs a tiered pipeline:
  1. JSON-LD schema parsing (`BlogPosting`, `NewsArticle`)
  2. OpenGraph & Twitter card metadata
  3. Trafilatura article main text extraction
  4. BeautifulSoup semantic HTML fallback
- Sanitizes output to prevent XSS vulnerabilities while retaining heading structures and paragraph blocks.

### D. Canonical Deduplication Engine (`app.services.deduplicator`)
- **Normalized Canonical URL**: Strips tracking parameters (`utm_*`, `ref`, `fbclid`) and trailing slashes.
- **SHA-256 Content Hash**: `hash(title + body_prefix + pubdate_str)`.
- **Deduplication Check**: Queries database by canonical URL, source URL, content hash, and title to prevent duplicate alerts.

### E. Exact Detection Delay Measurement (`app.services.strategy_engine`)
- **Formula**: `detection_delay_seconds = detected_at - publication_time`
- **Display String**: Human-formatted exact strings (`38 sec`, `3 min 12 sec`, `1 hr 02 min 08 sec`).
- **5-Minute Target Evaluator**: Flags `within_target = (delay <= 300)`.

### F. 100-Website Scale Engine (`app.workers.scale_engine`)
- Processes 100 concurrent competitor targets.
- **Concurrency Control**: Async worker pool bounded by `asyncio.Semaphore(15)`.
- **Fault Tolerance**: Isolated exception handlers ensure that DNS failures, timeouts, or 5xx HTTP errors on one target do not halt other workers.
- **Throughput Metrics**: Live CPM (Checks per minute), average check latency, and error retry state tracking.
