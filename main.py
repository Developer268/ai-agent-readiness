"""
main.py — FastAPI application for AI Agent Readiness Prototype
Run with: uvicorn main:app --reload
"""

import asyncio
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import dataclasses

from scanner import scan
from scoring import compute

app = FastAPI(
    title="AI Agent Readiness API",
    description="Scan a website and get its AI Agent Readiness Business Score.",
    version="0.1.0",
)

templates = Jinja2Templates(directory="templates")

# Serve static files if the folder exists
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/scan", response_class=HTMLResponse)
async def scan_domain(request: Request, domain: str = Form(...)):
    """Accept a domain from the form, scan it, and return the results page."""
    domain = domain.strip().lower()
    scan_result = await scan(domain)
    report = compute(scan_result)

    # Convert dataclasses to dicts for template
    subscores = [
        {
            "name": ss.name,
            "score": ss.score,
            "max_score": ss.max_score,
            "pct": int(ss.score),
            "passed": ss.passed,
            "failed": ss.failed,
        }
        for ss in report.subscores
    ]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "domain": report.domain,
            "overall": report.overall,
            "grade": report.grade,
            "subscores": subscores,
            "recommendations": report.recommendations,
        },
    )


@app.post("/api/scan")
async def api_scan(domain: str):
    """JSON API endpoint — returns the full score report."""
    domain = domain.strip().lower()
    scan_result = await scan(domain)
    report = compute(scan_result)
    return dataclasses.asdict(report)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
