import json

from app.llm.client import LLMClient
from app.models.claim import Claim
from app.models.evidence import Evidence


class ClaimExtractor:
    """Converts evidence records into traceable research claims."""

    def __init__(self):
        self.llm = LLMClient()

    def extract(
        self,
        evidence_records: list[Evidence],
    ) -> list[Claim]:
        """Extract research claims from a collection of evidence."""

        if not evidence_records:
            return []

        evidence_text = "\n\n".join(
            (
                f"EVIDENCE ID: {evidence.evidence_id}\n"
                f"CLAIM: {evidence.claim}\n"
                f"SUPPORTING TEXT: {evidence.extracted_text}\n"
                f"CONFIDENCE: {evidence.confidence}"
            )
            for evidence in evidence_records
        )

        prompt = f"""
You are a senior research analyst.

Convert the evidence below into concise, factual research claims.

EVIDENCE
{evidence_text}

Instructions:
- Use only information supported by the provided evidence.
- Do not introduce outside knowledge.
- Do not invent facts.
- Combine related evidence when it supports the same factual claim.
- Every claim must reference at least one evidence ID.
- A claim may reference multiple evidence IDs.
- Preserve important numerical values, dates, names, and conditions.
- Do not make predictions unless the evidence explicitly supports them.
- Confidence must be between 0.0 and 1.0.
- Status should be "supported".
- If the evidence does not support a meaningful claim, return an empty list.

Return ONLY valid JSON in this format:

[
    {{
        "statement": "Factual research claim",
        "evidence_ids": ["EVD-001"],
        "confidence": 0.0,
        "status": "supported"
    }}
]

Do not include markdown.
Do not include explanations outside the JSON.
"""

        response = self.llm.generate(prompt)

        try:
            claim_data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The claim extractor returned invalid JSON."
            ) from exc

        claims = []

        for index, item in enumerate(claim_data, start=1):
            claims.append(
                Claim(
                    claim_id=f"CLM-{index:03d}",
                    statement=item["statement"],
                    evidence_ids=item["evidence_ids"],
                    confidence=item["confidence"],
                    status=item["status"],
                )
            )

        return claims