import json

from app.llm.client import LLMClient
from app.models.source import Source


class CompetitiveIntelligenceExtractor:
    """Extracts structured competitive intelligence from source content."""

    def __init__(self):
        self.llm = LLMClient()

    def extract(self, source: Source, content: str) -> dict:
        if not content.strip():
            raise ValueError("Source content cannot be empty.")

        prompt = f"""
You are a competitive intelligence analyst.

Analyze the following source and extract only information explicitly
supported by the source.

SOURCE
Title: {source.title}
Publisher: {source.publisher}
URL: {source.url}

CONTENT
{content}

Extract the following where available:
- company or competitor name
- products or services
- pricing information or pricing signals
- key features or capabilities
- target customers or markets
- market positioning
- geographic presence
- notable competitive strengths

Rules:
- Do not invent information.
- Do not use outside knowledge.
- If information is unavailable, use an empty list or null.
- Preserve factual accuracy.
- Keep extracted information concise.
- Include the original source URL.

Return ONLY valid JSON in this format:

{{
    "company_name": "Company name or null",
    "products_services": [],
    "pricing_signals": [],
    "key_features": [],
    "target_customers": [],
    "positioning": [],
    "geographic_presence": [],
    "competitive_strengths": [],
    "source_url": "{source.url}"
}}

Do not include markdown.
Do not include explanations outside the JSON.
"""

        response = self.llm.generate(prompt)

        try:
            intelligence = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The competitive intelligence extractor returned invalid JSON."
            ) from exc

        return intelligence