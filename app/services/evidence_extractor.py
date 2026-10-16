import json

from app.llm.client import LLMClient
from app.models.evidence import Evidence
from app.models.source import Source


class EvidenceExtractor:
    """Extracts evidence-backed findings from multiple sources in batches."""

    def __init__(self):
        self.llm = LLMClient()

    def extract_batch(
        self,
        source_contents: list[tuple[Source, str]],
    ) -> list[Evidence]:
        """
        Extract evidence from multiple sources using a single LLM call.

        Each tuple contains:
            (Source, webpage_content)
        """

        if not source_contents:
            return []

        source_blocks = []

        for index, (source, content) in enumerate(
            source_contents,
            start=1,
        ):
            if not content.strip():
                continue

            source_blocks.append(
                f"""
SOURCE {index}

SOURCE TITLE:
{source.title}

PUBLISHER:
{source.publisher}

URL:
{source.url}

SOURCE TYPE:
{source.source_type}

CONTENT:
{content}
"""
            )

        if not source_blocks:
            return []

        combined_sources = "\n".join(source_blocks)

        prompt = f"""
You are an evidence extraction specialist for an enterprise
market research intelligence system.

Extract factual, evidence-backed findings from ALL sources below.

{combined_sources}

INSTRUCTIONS:

- Extract only information explicitly supported by the provided sources.
- Do not invent facts.
- Do not add outside knowledge.
- Keep evidence tied to the correct source.
- Focus on factual findings useful for market research.
- Each evidence item must contain one concise factual claim.
- Include relevant supporting text from the source.
- Preserve the exact source URL for every evidence item.
- Confidence must be between 0.0 and 1.0.
- Avoid duplicate evidence.
- If a source contains no useful factual evidence, do not create
  evidence for that source.

Return ONLY valid JSON in this format:

[
    {{
        "source_url": "https://example.com/source",
        "claim": "Factual claim supported by the source",
        "extracted_text": "Relevant supporting text from the source",
        "confidence": 0.0
    }}
]

IMPORTANT:
- source_url MUST exactly match one of the URLs provided above.
- Do not create URLs.
- Do not include markdown.
- Do not include explanations outside the JSON.
"""

        response = self.llm.generate(prompt)

        try:
            evidence_data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The evidence extractor returned invalid JSON."
            ) from exc

        # Map source URL → Source object.
        source_map = {
            source.url: source
            for source, _ in source_contents
        }

        evidence_records = []

        for item in evidence_data:

            source_url = item["source_url"]

            if source_url not in source_map:
                continue

            source = source_map[source_url]

            evidence_records.append(
                Evidence(
                    evidence_id="",
                    claim=item["claim"],
                    source_title=source.title,
                    source_url=source.url,
                    publication_date=source.publication_date,
                    extracted_text=item["extracted_text"],
                    source_type=source.source_type,
                    confidence=item["confidence"],
                )
            )

        # Assign globally unique evidence IDs.
        for index, evidence in enumerate(
            evidence_records,
            start=1,
        ):
            evidence.evidence_id = f"EVD-{index:03d}"

        return evidence_records

    def extract(
        self,
        source: Source,
        content: str,
    ) -> list[Evidence]:
        """
        Backward-compatible single-source extraction.

        Existing tests or components can still call:
            extractor.extract(source, content)
        """

        if not content.strip():
            raise ValueError(
                "Source content cannot be empty."
            )

        return self.extract_batch(
            [(source, content)]
        )