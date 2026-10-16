from app.models.claim import Claim
from app.models.report import ResearchReport
from app.services.report_exporter import ReportExporter


def main():
    print("\n" + "=" * 70)
    print("DOWNSTREAM PIPELINE INTEGRATION TEST")
    print("=" * 70)

    claims = [
        Claim(
            claim_id="CLM-001",
            statement=(
                "The market shows continued demand growth."
            ),
            evidence_ids=["EVD-001"],
            confidence=0.90,
            status="supported",
        ),
        Claim(
            claim_id="CLM-002",
            statement=(
                "Pricing varies significantly across product grades."
            ),
            evidence_ids=["EVD-002"],
            confidence=0.85,
            status="supported",
        ),
    ]

    print("\nClaims:", len(claims))

    report = ResearchReport(
        title="Indian Fruit Pulp Market Research",
        executive_summary=(
            "The research indicates continued market demand "
            "alongside differentiated pricing across product grades."
        ),
        key_findings=[
            claim.statement
            for claim in claims
        ],
        insights=[
            (
                "Market growth with pricing differentiation: "
                "continued demand growth exists alongside "
                "differentiated pricing across product grades."
            )
        ],
        risks=[
            "Pricing variability may affect market positioning."
        ],
        opportunities=[
            (
                "Growing demand may create opportunities "
                "for differentiated products."
            )
        ],
        contradictions=[
            (
                "Low-confidence potential conflict between "
                "market growth and pricing differentiation claims; "
                "the claims may describe different dimensions."
            )
        ],
        competitive_summary=[],
        conclusion=(
            "The research supports further investigation of "
            "market segments, pricing, and competitive positioning."
        ),
    )

    print("Insights:", len(report.insights))
    print("Contradictions:", len(report.contradictions))

    exporter = ReportExporter()

    report_path = exporter.export_markdown(
        report=report,
        output_path=(
            "reports/downstream_integration_test.md"
        ),
    )

    print("\nReport exported successfully:")
    print(report_path)

    print("\n" + "=" * 70)
    print("DOWNSTREAM PIPELINE TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()