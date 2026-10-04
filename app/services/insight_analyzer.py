import json

from app.llm.client import LLMClient
from app.models.claim import Claim
from app.models.contradiction import Contradiction
from app.models.insight import Insight


class InsightAnalyzer:
    """Analyzes validated claims and contradictions to generate research insights."""

    def __init__(self):
        self.llm = LLMClient()

    def analyze(
        self,
        claims: list[Claim],
        contradictions: list[Contradiction],
    ) -> list[Insight]:

        if not claims:
            return []

        claims_text = "\n\n".join(
            (
                f"CLAIM ID: {claim.claim_id}\n"
                f"STATEMENT: {claim.statement}\n"
                f"EVIDENCE IDS: {', '.join(claim.evidence_ids)}\n"
                f"CONFIDENCE: {claim.confidence}\n"
                f"STATUS: {claim.status}"
            )
            for claim in claims
        )

        contradictions_text = "\n\n".join(
            (
                f"CONTRADICTION ID: {contradiction.contradiction_id}\n"
                f"CLAIM A: {contradiction.claim_a_id}\n"
                f"CLAIM B: {contradiction.claim_b_id}\n"
                f"EXPLANATION: {contradiction.explanation}\n"
                f"SEVERITY: {contradiction.severity}\n"
                f"CONFIDENCE: {contradiction.confidence}"
            )
            for contradiction in contradictions
        )

        if not contradictions_text:
            contradictions_text = "No contradictions were detected."

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
- Identify patterns, trends, opportunities, risks, or market gaps only when
  they are reasonably supported by the provided claims.
- Every insight must reference at least one supporting claim ID.
- Do not treat a contradiction as resolved.
- If conflicting claims affect an insight, mention the uncertainty in the explanation.
- Keep each insight specific and useful for business research.
- Confidence must be between 0.0 and 1.0.
- Return an empty list if no meaningful insight can be supported.

Return ONLY valid JSON in this format:

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

        for index, item in enumerate(insight_data, start=1):
            insights.append(
                Insight(
                    insight_id=f"INS-{index:03d}",
                    title=item["title"],
                    explanation=item["explanation"],
                    supporting_claim_ids=item["supporting_claim_ids"],
                    confidence=item["confidence"],
                    implication=item["implication"],
                )
            )

        return insights