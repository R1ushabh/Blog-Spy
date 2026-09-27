# Evaluator Demo Walkthrough Guide

Follow this exact step-by-step sequence to demonstrate and evaluate all system criteria.

---

## 🎬 Step-by-Step Evaluator Script

### STEP 1: Open Dashboard
1. Navigate to `http://localhost:3000`.
2. Observe the KPI Cards:
   - **Monitored Websites**
   - **Articles Detected**
   - **Average Detection Delay** (exact seconds & human formatted string e.g. `3 min 12 sec`)
   - **System Health & Error Isolation**
3. Observe the real-time **SSE Stream Status Badge** (`LIVE SSE`).

---

### STEP 2: Controlled Demo Publishing Test
1. Click **Controlled Demo Site** on the sidebar or navigate to `http://localhost:3000/demo-site-test`.
2. Click the green button: **"Run Complete 1-Click Demo Pipeline"**.
3. Watch the automated trace execute:
   - Validates Acme Corp Demo Competitor
   - Automatically runs website analyzer discovering RSS (`/api/demo-site/rss.xml`) and Sitemap (`/api/demo-site/sitemap.xml`)
   - Publishes test article with publication timestamp
   - Triggers background worker monitoring check
   - Extracts title, body, author, images, and canonical URL
   - Computes exact detection delay
   - Emits real-time SSE notification
4. Click **View Live Dashboard Results** to observe the newly detected article card with exact delay badge (`✓ Within 5-min target`).

---

### STEP 3: Automatic Website Analysis
1. Navigate to **Competitors** (`http://localhost:3000/competitors`).
2. Click **Add Competitor Target**.
3. Enter any domain (e.g. `techcrunch.com` or `http://127.0.0.1:8000/api/demo-site`).
4. Click **Analyze & Save Competitor**.
5. Observe the interactive **Website Analysis Card**:
   - Shows discovered RSS feeds, Atom feeds, and XML sitemaps
   - Shows schema.org JSON-LD & canonical signals
   - Displays confidence ratings (RSS: High, Sitemap: High, Direct Page: Medium)
   - Displays strategy rationale string.

---

### STEP 4: 100-Website Scalability Test
1. Navigate to **100-Site Scale Test** (`http://localhost:3000/scale-test`).
2. Click **Seed 100 Sites** to populate 100 realistic mock competitor targets.
3. Click **Start Scale Engine**.
4. Observe live concurrency metrics:
   - Active Async Workers: 15
   - Throughput (CPM): Checks per minute
   - Processing Count & Average Check Duration (ms)
   - Successful Checks vs Isolated Failures
5. Review the **Architecture Explanation** section answering all 6 scale design questions.

---

### STEP 5: Academic Evidence & Compliance Audit
1. Navigate to **Evidence & Audit** (`http://localhost:3000/evidence`).
2. Review the 15-item academic compliance matrix.
3. Click on any requirement (e.g., **Exact Detection Delay & 5-Min Target** or **Canonical Duplicate Prevention**) to expand live empirical evidence fetched directly from system runtime.
