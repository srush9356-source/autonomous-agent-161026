import json

from app.llm.client import LLMClient
from app.models.claim import Claim
from app.models.contradiction import Contradiction


class ContradictionDetector:
    """Detects conflicts between research claims."""

    def __init__(self):
        self.llm = LLMClient()

    def detect(
        self,
        claims: list[Claim],
    ) -> list[Contradiction]:
        """Identify contradictions among research claims."""

        if len(claims) < 2:
            return []

        claims_text = "\n\n".join(
            (
                f"CLAIM ID: {claim.claim_id}\n"
                f"STATEMENT: {claim.statement}\n"
                f"EVIDENCE IDS: {', '.join(claim.evidence_ids)}\n"
                f"CONFIDENCE: {claim.confidence}"
            )
            for claim in claims
        )

        prompt = f"""
You are a research quality-control analyst.

Analyze the following research claims and identify genuine
contradictions between them.

CLAIMS
{claims_text}

Instructions:
- Compare claims based only on the information provided.
- Identify only genuine factual conflicts.
- Do not treat different wording as a contradiction.
- Do not treat claims as contradictory merely because they
  discuss different topics, periods, markets, regions, or metrics.
- Pay attention to dates, geographic scope, units, and definitions.
- Do not invent missing context.
- Do not resolve or choose between conflicting claims.
- Preserve both claims when a contradiction exists.
- If there are no genuine contradictions, return an empty list.
- Severity must be one of: "low", "medium", "high".
- Confidence must be between 0.0 and 1.0.

Return ONLY valid JSON in this format:

[
    {{
        "claim_a_id": "CLM-001",
        "claim_b_id": "CLM-002",
        "explanation": "Why these claims genuinely conflict",
        "severity": "medium",
        "confidence": 0.0
    }}
]

Do not include markdown.
Do not include explanations outside the JSON.
"""

        response = self.llm.generate(prompt)

        try:
            contradiction_data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The contradiction detector returned invalid JSON."
            ) from exc

        contradictions = []

        for index, item in enumerate(contradiction_data, start=1):
            contradictions.append(
                Contradiction(
                    contradiction_id=f"CON-{index:03d}",
                    claim_a_id=item["claim_a_id"],
                    claim_b_id=item["claim_b_id"],
                    explanation=item["explanation"],
                    severity=item["severity"],
                    confidence=item["confidence"],
                )
            )

        return contradictions