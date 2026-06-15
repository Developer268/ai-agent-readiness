# 🤖 AI Agent Readiness Scanner

> **Research Prototype — Semester 2 | Master in IT Management, UPB**
> Student: Ion Darius Alexandru

A SaaS prototype that scans any website and computes a multi-dimensional **AI Agent Readiness Business Score (0–100)**. The platform goes beyond Cloudflare’s free one-off scanner by providing structured subscores, actionable recommendations, and a clean dashboard — laying the foundation for a business-grade benchmarking tool.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Domain scanning** | Checks 7 agent-readiness signals concurrently |
| **Scoring engine** | Weighted subscores across 4 dimensions |
| **Dashboard** | Clean dark-mode UI with progress bars & checklists |
| **REST API** | JSON endpoint at `POST /api/scan` |
| **Fast** | Async scanning with `httpx` — results in < 5 s |

---

## 📊 Score Dimensions

| Dimension | Weight | Signals checked |
|---|---|---|
| Discoverability | 30% | `robots.txt`, XML sitemap |
| Content Accessibility | 25% | `llms.txt`, Markdown content negotiation |
| Bot Access & Governance | 25% | `robots.txt` agent policy, HTTP Link header (RFC 8288) |
| Protocol Readiness | 20% | OAuth metadata (RFC 8414), API Catalog (RFC 9727) |

**Grade scale:** A ≥ 80 · B ≥ 60 · C ≥ 40 · D ≥ 20 · F < 20

---

## 📁 Project Structure

```
ai-agent-readiness/
├── main.py              # FastAPI app (routes + template rendering)
├── scanner.py           # Async scanning engine (7 checks)
├── scoring.py           # Scoring & recommendation engine
├── templates/
│   └── index.html       # Jinja2 dashboard template
├── requirements.txt     # Python dependencies
└── .gitignore
```

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/Developer268/ai-agent-readiness.git
cd ai-agent-readiness

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
uvicorn main:app --reload

# 4. Open the dashboard
# http://localhost:8000
```

---

## 🔌 API Usage

### Scan via browser form
`POST /scan` with form field `domain=example.com`

### Scan via JSON API
```bash
curl -X POST "http://localhost:8000/api/scan?domain=example.com"
```

Example response:
```json
{
  "domain": "example.com",
  "overall": 37.5,
  "grade": "D",
  "subscores": [
    {"name": "Discoverability", "score": 50, "passed": ["robots.txt present"], "failed": ["XML sitemap missing"]},
    ...
  ],
  "recommendations": [
    "Publish a /sitemap.xml so agents can enumerate your content.",
    ...
  ]
}
```

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, FastAPI, uvicorn
- **Scanning:** httpx (async HTTP), BeautifulSoup4
- **Templating:** Jinja2
- **Frontend:** Vanilla HTML/CSS (dark mode, responsive)

---

## 📚 Academic Context

This prototype is developed as part of **Research Report 2** for the Master’s programme in IT Management / Technological Entrepreneurship and Management at Politehnica University of Bucharest.

The research question: *How can AI Agent Readiness scores be transformed into a sustainable SaaS business that helps organisations systematically measure, compare, and improve the agent-readiness of their websites?*

Semester 2 focus: technology selection, preliminary prototype, engineering experiments, and feasibility confirmation.

---

## 📅 Roadmap

- [ ] MCP / WebMCP descriptor detection
- [ ] Historical score tracking (PostgreSQL)
- [ ] Industry benchmarking dashboard
- [ ] User accounts & multi-domain portfolio
- [ ] CI/CD gate integration
- [ ] Comparison study vs. Cloudflare Agent Readiness scanner

---

*Built with ❤️ in Bucharest, Romania · June 2026*
