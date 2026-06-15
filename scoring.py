"""
scoring.py — AI Agent Readiness Scoring Engine
Maps ScanResult fields into subscores and an overall 0-100 score.
"""

from dataclasses import dataclass
from scanner import ScanResult


@dataclass
class SubScore:
    name: str
    score: float          # 0-100
    max_score: float
    passed: list
    failed: list


@dataclass
class ScoreReport:
    domain: str
    overall: float        # 0-100, rounded to 1 decimal
    grade: str            # A / B / C / D / F
    subscores: list       # list[SubScore]
    recommendations: list # list[str]


# --- Weights (must sum to 100) ---
WEIGHTS = {
    "Discoverability":       30,
    "Content Accessibility": 25,
    "Bot Access & Governance": 25,
    "Protocol Readiness":    20,
}


def _grade(score: float) -> str:
    if score >= 80:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 40:
        return "C"
    elif score >= 20:
        return "D"
    return "F"


def compute(result: ScanResult) -> ScoreReport:
    """Compute subscores and overall score from a ScanResult."""
    subscores = []
    recommendations = []

    # --- 1. Discoverability (robots.txt + sitemap) ---
    passed, failed = [], []
    raw = 0
    if result.robots_txt_present:
        raw += 50
        passed.append("robots.txt present")
    else:
        failed.append("robots.txt missing")
        recommendations.append(
            "Add a /robots.txt file to help agents understand crawl rules."
        )
    if result.sitemap_present:
        raw += 50
        passed.append("XML sitemap present")
    else:
        failed.append("XML sitemap missing")
        recommendations.append(
            "Publish a /sitemap.xml so agents can enumerate your content."
        )
    subscores.append(SubScore("Discoverability", raw, 100, passed, failed))

    # --- 2. Content Accessibility (llms.txt + markdown) ---
    passed, failed = [], []
    raw = 0
    if result.llms_txt_present:
        raw += 70
        passed.append("llms.txt present")
    else:
        failed.append("llms.txt missing")
        recommendations.append(
            "Create /llms.txt to expose structured guidance for LLM agents "
            "(see https://llmstxt.org)."
        )
    if result.markdown_available:
        raw += 30
        passed.append("Markdown content negotiation supported")
    else:
        failed.append("No Markdown content negotiation")
        recommendations.append(
            "Support Accept: text/markdown so agents can request clean, "
            "structured content."
        )
    subscores.append(SubScore("Content Accessibility", raw, 100, passed, failed))

    # --- 3. Bot Access & Governance (robots.txt allows agents + link header) ---
    passed, failed = [], []
    raw = 0
    if result.robots_txt_allows_agents:
        raw += 60
        passed.append("robots.txt allows AI agents")
    else:
        failed.append("robots.txt blocks all bots (Disallow: /)")
        recommendations.append(
            "Review your robots.txt — a blanket Disallow: / blocks AI agents "
            "from accessing your site."
        )
    if result.link_header_present:
        raw += 40
        passed.append("HTTP Link header present (RFC 8288)")
    else:
        failed.append("No HTTP Link header")
        recommendations.append(
            "Add RFC 8288 Link headers to expose related resources to agents."
        )
    subscores.append(SubScore("Bot Access & Governance", raw, 100, passed, failed))

    # --- 4. Protocol Readiness (OAuth metadata + API catalog) ---
    passed, failed = [], []
    raw = 0
    if result.oauth_metadata_present:
        raw += 50
        passed.append("OAuth / OIDC metadata published (RFC 8414)")
    else:
        failed.append("No OAuth / OIDC metadata at .well-known")
        recommendations.append(
            "Publish /.well-known/oauth-authorization-server (RFC 8414) so "
            "agents can discover your authentication endpoints."
        )
    if result.api_catalog_present:
        raw += 50
        passed.append("API catalog published (RFC 9727)")
    else:
        failed.append("No API catalog at .well-known/api-catalog")
        recommendations.append(
            "Publish /.well-known/api-catalog (RFC 9727) to help agents "
            "discover your available APIs."
        )
    subscores.append(SubScore("Protocol Readiness", raw, 100, passed, failed))

    # --- Overall weighted score ---
    overall = sum(
        (ss.score / 100) * WEIGHTS[ss.name]
        for ss in subscores
    )
    overall = round(overall, 1)

    return ScoreReport(
        domain=result.domain,
        overall=overall,
        grade=_grade(overall),
        subscores=subscores,
        recommendations=recommendations,
    )
