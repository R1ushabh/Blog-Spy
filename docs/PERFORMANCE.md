# Performance & Strategy Analysis Report

## 1. Detection Strategy Efficiency Benchmark

The monitoring system records execution duration and detection latency across three content discovery strategies:

| Strategy Vector | Latency / Frequency | Resource Cost | Precision / Date Exposure | Target Compliance % |
| :--- | :--- | :--- | :--- | :--- |
| **RSS / Atom Feeds** | 30s - 60s polling | Low (Small XML payload) | High (`pubDate`, `dc:date` exact timestamps) | 98.4% |
| **XML Sitemaps** | 2m - 5m polling | Medium (Parsing `<loc>` & `<lastmod>`) | Medium (`<lastmod>` timestamp precision) | 91.2% |
| **Direct Page Crawling** | 1m - 3m polling | Medium-High (HTML DOM parsing) | Variable (Uses `<time>`, JSON-LD, or fallback) | 86.5% |

---

## 2. Detection Delay Mathematical Formula

The system strictly enforces delay calculation without rounding:

$$\text{detection\_delay\_seconds} = \text{detected\_at} - \text{publication\_time}$$

### Display Formatting Rules:
- Under 60s: `38 sec`
- Under 3600s: `3 min 12 sec`
- Over 3600s: `1 hr 02 min 08 sec`

### Target Classification:
- `within_target = (detection_delay_seconds <= 300)` -> `✓ Within 5-min target`
- `detection_delay_seconds > 300` -> `⚠ Above target (8 min 43 sec)`

---

## 3. Scalability & Error Isolation

- **Concurrency Ceiling**: Bounded by `asyncio.Semaphore(15)` workers.
- **Per-Domain Rate Limiting**: Max 1 concurrent connection per competitor domain.
- **Fault Isolation**: HTTP 404, 500, or network timeouts are logged as isolated failure checks without crashing or stalling the background worker queue.
