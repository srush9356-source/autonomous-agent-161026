import json

from app.llm.client import LLMClient
from app.models.claim import Claim
from app.models.contradiction import Contradiction
from app.models.insight import Insight
from app.models.report import ResearchReport


class ReportGenerator:
    """Generates a structured executive research report."""

    def __init__(self):
        self.llm = LLMClient()

    def generate(
        self,
        topic: str,
        claims: list[Claim],
        insights: list[Insight],
        contradictions: list[Contradiction],
        competitive_intelligence: list[dict],
    ) -> ResearchReport:

        if not claims:
            raise ValueError("At least one claim is required.")

        claims_text = "\n\n".join(
            (
                f"CLAIM ID: {claim.claim_id}\n"
                f"STATEMENT: {claim.statement}\n"
                f"CONFIDENCE: {claim.confidence}\n"
                f"EVIDENCE IDS: {', '.join(claim.evidence_ids)}"
            )
            for claim in claims
        )

        insights_text = "\n\n".join(
            (
                f"INSIGHT ID: {insight.insight_id}\n"
                f"TITLE: {insight.title}\n"
                f"EXPLANATION: {insight.explanation}\n"
                f"SUPPORTING CLAIMS: {', '.join(insight.supporting_claim_ids)}\n"
                f"CONFIDENCE: {insight.confidence}\n"
                f"IMPLICATION: {insight.implication}"
            )
            for insight in insights
        )

        contradictions_text = "\n\n".join(
            (
                f"CONTRADICTION ID: {item.contradiction_id}\n"
                f"CLAIM A: {item.claim_a_id}\n"
                f"CLAIM B: {item.claim_b_id}\n"
                f"EXPLANATION: {item.explanation}\n"
                f"SEVERITY: {item.severity}\n"
                f"CONFIDENCE: {item.confidence}"
            )
            for item in contradictions
        )

        if not contradictions_text:
            contradictions_text = "No contradictions were detected."

        competitive_text = "\n\n".join(
            json.dumps(item, ensure_ascii=False)
            for item in competitive_intelligence
        )

        if not competitive_text:
            competitive_text = "No competitive intelligence was available."

        prompt = f"""
You are a senior executive research analyst.

Create an evidence-based executive research report for:

TOPIC:
{topic}

RESEARCH CLAIMS:
{claims_text}

RESEARCH INSIGHTS:
{insights_text}

DETECTED CONTRADICTIONS:
{contradictions_text}

COMPETITIVE INTELLIGENCE:
{competitive_text}

Instructions:
- Use ONLY the information provided above.
- Do not invent facts, numbers, companies, competitors, or market information.
- Clearly distinguish findings from uncertainty.
- Do not resolve contradictions unless the provided information supports doing so.
- Key findings must summarize the most important research claims.
- Insights should summarize meaningful strategic implications.
- Risks should reflect uncertainty, contradictions, or explicitly identified risks.
- Opportunities should reflect explicitly supported opportunities.
- Competitive summary should use only the provided competitive intelligence.
- Keep the report concise and executive-friendly.
- Do not include unsupported recommendations.

Return ONLY valid JSON in this format:

{{
    "title": "Executive Research Report: ...",
    "executive_summary": "Concise executive summary.",
    "key_findings": [
        "Finding 1",
        "Finding 2"
    ],
    "insights": [
        "Insight 1"
    ],
    "risks": [
        "Risk 1"
    ],
    "opportunities": [
        "Opportunity 1"
    ],
    "contradictions": [
        "Contradiction or uncertainty 1"
    ],
    "competitive_summary": [
        "Competitive finding 1"
    ],
    "conclusion": "Evidence-based conclusion."
}}

Do not include markdown.
Do not include explanations outside the JSON.
"""

        response = self.llm.generate(prompt)

        try:
            report_data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The report generator returned invalid JSON."
            ) from exc

        return ResearchReport(**report_data)