import json

from app.llm.client import LLMClient
from app.models.claim import Claim
from app.models.contradiction import Contradiction
from app.models.insight import Insight


class InsightAnalyzer:
    """
    Analyzes research claims and contradictions to generate
    evidence-backed strategic insights.
    """

    def __init__(self):
        self.llm = LLMClient()

    def analyze(
        self,
        claims: list[Claim],
        contradictions: list[Contradiction],
        max_claims: int = 60,
    ) -> list[Insight]:

        if not claims:
            return []

        # Keep the strongest claims so the insight prompt
        # remains bounded.
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
                f"CONFIDENCE: {claim.confidence}\n"
                f"STATUS: {claim.status}"
            )
            for claim in selected_claims
        )

        # Only include contradictions that reference the
        # claims being analyzed.
        selected_claim_ids = {
            claim.claim_id
            for claim in selected_claims
        }

        selected_contradictions = [
            contradiction
            for contradiction in contradictions
            if (
                contradiction.claim_a_id
                in selected_claim_ids
                and
                contradiction.claim_b_id
                in selected_claim_ids
            )
        ]

        contradictions_text = "\n\n".join(
            (
                f"CONTRADICTION ID: "
                f"{contradiction.contradiction_id}\n"
                f"CLAIM A: "
                f"{contradiction.claim_a_id}\n"
                f"CLAIM B: "
                f"{contradiction.claim_b_id}\n"
                f"EXPLANATION: "
                f"{contradiction.explanation}\n"
                f"SEVERITY: "
                f"{contradiction.severity}\n"
                f"CONFIDENCE: "
                f"{contradiction.confidence}"
            )
            for contradiction in selected_contradictions
        )

        if not contradictions_text:
            contradictions_text = (
                "No contradictions were detected."
            )

        prompt = f"""
You are a senior market research and strategic intelligence analyst.

Analyze the validated research claims and detected contradictions below.

CLAIMS
{claims_text}

CONTRADICTIONS
{contradictions_text}

Your task is to identify meaningful research insights.

Instructions:
- Use only the information provided in the claims and contradictions.
- Do not invent facts.
- Do not introduce outside knowledge.
- Identify patterns, trends, opportunities, risks, or market gaps only
  when reasonably supported by the provided claims.
- Every insight must reference at least one supporting claim ID.
- Do not treat a contradiction as resolved.
- If conflicting claims affect an insight, mention the uncertainty.
- Keep each insight specific and useful for business research.
- Avoid repeating the same insight.
- Confidence must be between 0.0 and 1.0.
- Return an empty list if no meaningful insight can be supported.

Return ONLY valid JSON:

[
    {{
        "title": "Short insight title",
        "explanation": "Evidence-based explanation of the insight.",
        "supporting_claim_ids": ["CLM-001"],
        "confidence": 0.0,
        "implication": "Potential business or strategic implication."
    }}
]

Do not include markdown.
Do not include explanations outside the JSON.
"""

        response = self.llm.generate(prompt)

        try:
            insight_data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The insight analyzer returned invalid JSON."
            ) from exc

        insights = []

        for item in insight_data:

            supporting_claim_ids = item.get(
                "supporting_claim_ids",
                [],
            )

            # Keep only valid claim references.
            valid_supporting_ids = [
                claim_id
                for claim_id in supporting_claim_ids
                if claim_id in selected_claim_ids
            ]

            if not valid_supporting_ids:
                continue

            insights.append(
                Insight(
                    insight_id=(
                        f"INS-{len(insights) + 1:03d}"
                    ),
                    title=item["title"],
                    explanation=item["explanation"],
                    supporting_claim_ids=(
                        valid_supporting_ids
                    ),
                    confidence=float(
                        item["confidence"]
                    ),
                    implication=item["implication"],
                )
            )

        return insights