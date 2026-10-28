import json
import re

from app.llm.client import LLMClient
from app.models.evidence import Evidence
from app.models.source import Source


class EvidenceExtractor:
    """Extract evidence-backed findings from multiple sources."""

    def __init__(self):
        self.llm = LLMClient()

    def extract_batch(
        self,
        source_contents: list[tuple[Source, str]],
    ) -> list[Evidence]:

        if not source_contents:
            return []

        source_blocks = []

        for index, (source, content) in enumerate(
            source_contents,
            start=1,
        ):
            if not content or not content.strip():
                continue

            # Limit each source's input to reduce token usage.
            content = content[:7000]

            source_blocks.append(
                f"""
SOURCE {index}
TITLE: {source.title}
PUBLISHER: {source.publisher}
URL: {source.url}
TYPE: {source.source_type}

CONTENT:
{content}
"""
            )

        if not source_blocks:
            return []

        combined_sources = "\n".join(source_blocks)

        prompt = f"""
You are an evidence extraction specialist.

Extract concise factual findings supported by these sources.
Do not use outside knowledge or invent facts.
Every source_url must exactly match a supplied source URL.
Include relevant supporting text.
Confidence must be between 0 and 1.
Avoid duplicates.

SOURCES:
{combined_sources}

Return ONLY a JSON array in this format:
[
  {{
    "source_url": "https://example.com/source",
    "claim": "A concise factual claim",
    "extracted_text": "Supporting source text",
    "confidence": 0.8
  }}
]

If no useful evidence exists, return [].
Do not include markdown or explanations.
"""

        try:
            response = self.llm.generate(prompt)
        except Exception as exc:
            print(f"Warning: Evidence extraction failed: {exc}")
            return []

        try:
            cleaned = response.strip()

            # Remove optional Markdown code fences.
            cleaned = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                cleaned,
                flags=re.IGNORECASE,
            ).strip()

            evidence_data = json.loads(cleaned)

            if not isinstance(evidence_data, list):
                raise ValueError("Expected a JSON array.")

        except (json.JSONDecodeError, ValueError, TypeError):
            print(
                "Warning: Evidence extractor returned invalid JSON. "
                "Skipping this batch."
            )
            return []

        source_map = {
            source.url: source
            for source, content in source_contents
            if content and content.strip()
        }

        evidence_records = []
        seen_items = set()

        for item in evidence_data:
            if not isinstance(item, dict):
                continue

            source_url = item.get("source_url")
            claim = item.get("claim")
            extracted_text = item.get("extracted_text")

            if source_url not in source_map:
                continue

            if not isinstance(claim, str) or not claim.strip():
                continue

            if (
                not isinstance(extracted_text, str)
                or not extracted_text.strip()
            ):
                continue

            try:
                confidence = float(item.get("confidence", 0.5))
            except (TypeError, ValueError):
                confidence = 0.5

            confidence = max(0.0, min(1.0, confidence))

            unique_key = (
                source_url,
                claim.strip().casefold(),
            )

            if unique_key in seen_items:
                continue

            seen_items.add(unique_key)
            source = source_map[source_url]

            evidence_records.append(
                Evidence(
                    evidence_id="",
                    claim=claim.strip(),
                    source_title=source.title,
                    source_url=source.url,
                    publication_date=source.publication_date,
                    extracted_text=extracted_text.strip(),
                    source_type=source.source_type,
                    confidence=confidence,
                )
            )

        return evidence_records

    def extract(
        self,
        source: Source,
        content: str,
    ) -> list[Evidence]:

        if not content or not content.strip():
            return []

        return self.extract_batch([(source, content)])