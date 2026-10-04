from app.models.claim import Claim
from app.models.contradiction import Contradiction
from app.models.insight import Insight
from app.services.report_generator import ReportGenerator


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

insights = [
    Insight(
        insight_id="INS-001",
        title="Growing domestic and export demand",
        explanation="Increasing domestic and export demand indicates an expanding opportunity for processed fruit products.",
        supporting_claim_ids=["CLM-001", "CLM-002"],
        confidence=0.88,
        implication="Producers can evaluate capacity expansion and export-market development.",
    )
]

contradictions = [
    Contradiction(
        contradiction_id="CON-001",
        claim_a_id="CLM-001",
        claim_b_id="CLM-003",
        explanation="Available sources differ in their reported market growth estimates.",
        severity="medium",
        confidence=0.80,
    )
]

competitive_intelligence = [
    {
        "company_name": "Example Food Company",
        "products_services": ["Mango pulp", "Guava pulp"],
        "pricing_signals": ["Pricing available through direct quotation"],
        "key_features": ["Bulk supply", "Consistent quality"],
        "target_customers": ["Food and beverage manufacturers"],
        "positioning": ["Quality and reliable supply"],
        "geographic_presence": ["Domestic and international markets"],
        "competitive_strengths": ["Consistent quality", "Reliable supply"],
        "source_url": "https://example.com",
    }
]


generator = ReportGenerator()

report = generator.generate(
    topic="Indian Fruit Pulp Market",
    claims=claims,
    insights=insights,
    contradictions=contradictions,
    competitive_intelligence=competitive_intelligence,
)

print("\nEXECUTIVE RESEARCH REPORT\n")
print(f"Title: {report.title}")
print(f"\nExecutive Summary:\n{report.executive_summary}")

print("\nKey Findings:")
for item in report.key_findings:
    print(f"- {item}")

print("\nInsights:")
for item in report.insights:
    print(f"- {item}")

print("\nRisks:")
for item in report.risks:
    print(f"- {item}")

print("\nOpportunities:")
for item in report.opportunities:
    print(f"- {item}")

print("\nContradictions:")
for item in report.contradictions:
    print(f"- {item}")

print("\nCompetitive Summary:")
for item in report.competitive_summary:
    print(f"- {item}")

print(f"\nConclusion:\n{report.conclusion}")