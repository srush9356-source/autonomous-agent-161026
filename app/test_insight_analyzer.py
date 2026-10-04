from app.models.claim import Claim
from app.models.contradiction import Contradiction
from app.services.insight_analyzer import InsightAnalyzer


claims = [
    Claim(
        claim_id="CLM-001",
        statement="The Indian fruit pulp market is experiencing increasing demand.",
        evidence_ids=["EVD-001"],
        confidence=0.90,
        status="supported",
    ),
    Claim(
        claim_id="CLM-002",
        statement="Export demand for processed fruit products is increasing.",
        evidence_ids=["EVD-002"],
        confidence=0.85,
        status="supported",
    ),
    Claim(
        claim_id="CLM-003",
        statement="Market growth estimates differ across available research sources.",
        evidence_ids=["EVD-003"],
        confidence=0.80,
        status="supported",
    ),
]

contradictions = [
    Contradiction(
        contradiction_id="CON-001",
        claim_a_id="CLM-001",
        claim_b_id="CLM-003",
        explanation="The claims provide different perspectives on the reported market growth situation.",
        severity="medium",
        confidence=0.75,
    )
]


analyzer = InsightAnalyzer()

insights = analyzer.analyze(
    claims=claims,
    contradictions=contradictions,
)

print("\nGenerated Insights:\n")

for insight in insights:
    print(f"Insight ID: {insight.insight_id}")
    print(f"Title: {insight.title}")
    print(f"Explanation: {insight.explanation}")
    print(f"Supporting Claims: {insight.supporting_claim_ids}")
    print(f"Confidence: {insight.confidence}")
    print(f"Implication: {insight.implication}")
    print("-" * 60)