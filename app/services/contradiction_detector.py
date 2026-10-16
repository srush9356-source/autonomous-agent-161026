import json

from app.llm.client import LLMClient
from app.models.claim import Claim
from app.models.contradiction import Contradiction


class ContradictionDetector:
    """Detects genuine conflicts between research claims."""

    def __init__(self):
        self.llm = LLMClient()

    def detect(
        self,
        claims: list[Claim],
        max_claims: int = 60,
    ) -> list[Contradiction]:
        """
        Identify genuine contradictions among research claims.

        Claims are limited to the strongest available claims to keep
        the analysis request bounded.
        """

        if len(claims) < 2:
            return []

        # Keep the highest-confidence claims.
        selected_claims = sorted(
            claims,
            key=lambda claim: claim.confidence,
            reverse=True,
        )[:max_claims]

        claims_text = "\n\n".join(
            (
                f"CLAIM ID: {claim.claim_id}\n"
                f"STATEMENT: {claim.statement}\n"
                f"EVIDENCE IDS: "
                f"{', '.join(claim.evidence_ids)}\n"
                f"CONFIDENCE: {claim.confidence}"
            )
            for claim in selected_claims
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
- Do not treat claims as contradictory merely because they discuss
  different topics, periods, markets, regions, or metrics.
- Pay attention to dates, geographic scope, units, and definitions.
- Do not invent missing context.
- Do not resolve or choose between conflicting claims.
- Preserve both claims when a contradiction exists.
- Severity must be one of: "low", "medium", "high".
- Confidence must be between 0.0 and 1.0.
- Only reference claim IDs that appear in the input.
- If there are no genuine contradictions, return an empty list.

Return ONLY valid JSON:

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

        valid_claim_ids = {
            claim.claim_id
            for claim in selected_claims
        }

        contradictions = []

        for item in contradiction_data:

            claim_a_id = item.get("claim_a_id")
            claim_b_id = item.get("claim_b_id")

            if claim_a_id not in valid_claim_ids:
                continue

            if claim_b_id not in valid_claim_ids:
                continue

            contradictions.append(
                Contradiction(
                    contradiction_id=(
                        f"CON-{len(contradictions) + 1:03d}"
                    ),
                    claim_a_id=claim_a_id,
                    claim_b_id=claim_b_id,
                    explanation=item["explanation"],
                    severity=item["severity"],
                    confidence=float(
                        item["confidence"]
                    ),
                )
            )

        return contradictions