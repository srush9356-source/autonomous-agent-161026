import json

from app.llm.client import LLMClient
from app.models.evidence import Evidence
from app.models.source import Source


class EvidenceExtractor:
    """Extracts evidence-backed findings from source content."""

    def __init__(self):
        self.llm = LLMClient()

    def extract(
        self,
        source: Source,
        content: str,
    ) -> list[Evidence]:
        """Extract structured evidence from source content."""

        if not content.strip():
            raise ValueError("Source content cannot be empty.")

        prompt = f"""
You are an evidence extraction specialist for an enterprise
market research system.

Extract factual, evidence-backed findings from the source below.

SOURCE
Title: {source.title}
Publisher: {source.publisher}
URL: {source.url}

CONTENT
{content}

Instructions:
- Extract only information explicitly supported by the source.
- Do not invent facts.
- Do not add outside knowledge.
- Focus on factual findings useful for market research.
- Each evidence item must contain a concise factual claim.
- Include the relevant supporting text from the source.
- Confidence must be between 0.0 and 1.0.
- If the source contains no useful factual evidence, return an empty list.

Return ONLY valid JSON in this format:

[
    {{
        "claim": "Factual claim supported by the source",
        "extracted_text": "Relevant supporting text from the source",
        "confidence": 0.0
    }}
]

Do not include markdown.
Do not include explanations outside the JSON.
"""

        response = self.llm.generate(prompt)

        try:
            evidence_data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The evidence extractor returned invalid JSON."
            ) from exc

        evidence_records = []

        for index, item in enumerate(evidence_data, start=1):
            evidence_records.append(
                Evidence(
                    evidence_id=f"EVD-{index:03d}",
                    claim=item["claim"],
                    source_title=source.title,
                    source_url=source.url,
                    publication_date=source.publication_date,
                    extracted_text=item["extracted_text"],
                    source_type=source.source_type,
                    confidence=item["confidence"],
                )
            )

        return evidence_records