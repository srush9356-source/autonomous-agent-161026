import json
import re

from app.llm.client import LLMClient
from app.models.claim import Claim
from app.models.contradiction import Contradiction


class ContradictionDetector:
    """Detect genuine conflicts between research claims."""

    def __init__(self):
        self.llm = LLMClient()
        self.last_status = "not_started"
        self.last_error = None

    def detect(
        self,
        claims: list[Claim],
        max_claims: int = 20,
    ) -> list[Contradiction]:

        self.last_status = "failed"
        self.last_error = None

        if len(claims) < 2:
            self.last_status = "completed"
            return []

        selected_claims = sorted(
            claims,
            key=lambda claim: claim.confidence,
            reverse=True,
        )[:max_claims]

        claims_text = "\n".join(
            (
                f"{claim.claim_id}: {claim.statement} "
                f"[Evidence: {', '.join(claim.evidence_ids)}]"
            )
            for claim in selected_claims
        )

        prompt = f"""
Identify only genuine factual contradictions between these claims.

Claims:
{claims_text}

Rules:
- Compare dates, regions, units, and definitions carefully.
- Different topics or non-conflicting claims are not contradictions.
- Never invent facts or claim IDs.
- Severity must be low, medium, or high.
- Confidence must be between 0 and 1.
- Return an empty JSON array if no contradictions exist.

Return ONLY a JSON array in this format:
[
  {{
    "claim_a_id": "CLM-001",
    "claim_b_id": "CLM-002",
    "explanation": "Brief explanation",
    "severity": "medium",
    "confidence": 0.8
  }}
]
"""

        try:
            response = self.llm.generate(prompt)

            if not isinstance(response, str) or not response.strip():
                raise ValueError(
                    "The LLM returned an empty response."
                )

        except Exception as exc:
            self.last_status = "failed"
            self.last_error = str(exc)

            print(
                "Warning: Contradiction detection failed: "
                f"{exc}"
            )
            return []

        try:
            cleaned = response.strip()

            cleaned = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                cleaned,
                flags=re.IGNORECASE,
            ).strip()

            contradiction_data = json.loads(cleaned)

            if not isinstance(contradiction_data, list):
                raise ValueError(
                    "Expected a JSON array of contradictions."
                )

        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            self.last_status = "failed"
            self.last_error = str(exc)

            print(
                "Warning: Invalid JSON from contradiction detector: "
                f"{exc}"
            )
            return []

        valid_claim_ids = {
            claim.claim_id for claim in selected_claims
        }

        contradictions = []
        seen_pairs = set()

        for item in contradiction_data:
            if not isinstance(item, dict):
                continue

            claim_a_id = item.get("claim_a_id")
            claim_b_id = item.get("claim_b_id")

            if claim_a_id not in valid_claim_ids:
                continue

            if claim_b_id not in valid_claim_ids:
                continue

            if claim_a_id == claim_b_id:
                continue

            pair = tuple(sorted((claim_a_id, claim_b_id)))

            if pair in seen_pairs:
                continue

            severity = str(
                item.get("severity", "low")
            ).lower()

            if severity not in {"low", "medium", "high"}:
                severity = "low"

            try:
                confidence = float(
                    item.get("confidence", 0.0)
                )
            except (TypeError, ValueError):
                confidence = 0.0

            confidence = max(0.0, min(1.0, confidence))

            explanation = item.get("explanation")

            if (
                not isinstance(explanation, str)
                or not explanation.strip()
            ):
                continue

            seen_pairs.add(pair)

            contradictions.append(
                Contradiction(
                    contradiction_id=(
                        f"CON-{len(contradictions) + 1:03d}"
                    ),
                    claim_a_id=claim_a_id,
                    claim_b_id=claim_b_id,
                    explanation=explanation.strip(),
                    severity=severity,
                    confidence=confidence,
                )
            )

        # An empty, valid JSON array is a successful check.
        self.last_status = "completed"
        return contradictions