"""LLM integration for root-cause analysis via the Gemini API (google-genai SDK)."""
from __future__ import annotations

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()  # loads GEMINI_API_KEY from .env


def _get_client(api_key: str | None = None) -> genai.Client:
    """Return a Gemini client, using the provided key or GEMINI_API_KEY env var."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "Set the GEMINI_API_KEY environment variable or pass api_key= explicitly."
        )
    return genai.Client(api_key=key)


def build_rca_prompt(incident: dict) -> str:
    evidence = "\n".join(
        f'- {e["timestamp"]}: {e["signal"]} ({e["detail"]})'
        for e in incident["evidence"][:20]
    )
    return (
        "You are a cautious Solr SRE. Analyze ONLY the supplied evidence.\n"
        f"Incident: {incident['incident_id']} on {incident['node']}, "
        f"classification candidate: {incident['classification']}.\n"
        f"Evidence:\n{evidence}\n\n"
        "Return: (1) likely root cause, (2) user impact, (3) safe first remediation, "
        "(4) confidence. If evidence is insufficient, say so. "
        "Do not claim unlisted metrics, causes, or actions."
    )


def run_rca(
    incident: dict,
    *,
    model: str = "gemini-3.1-flash-lite",
    api_key: str | None = None,
) -> str:
    """Build the RCA prompt for *incident* and send it to Gemini.

    Returns the model's response text.
    """
    client = _get_client(api_key)
    prompt = build_rca_prompt(incident)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text
