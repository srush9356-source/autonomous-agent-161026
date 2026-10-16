from app.models.report import ResearchReport
from app.services.pdf_report_exporter import PDFReportExporter


report = ResearchReport(
    title="Indian Fruit Pulp Market Research",
    executive_summary=(
        "The research indicates continued market demand "
        "alongside differentiated pricing across product grades."
    ),
    key_findings=[
        "The market shows continued demand growth.",
        "Pricing varies significantly across product grades.",
    ],
    insights=[
        (
            "Market growth with pricing differentiation: "
            "continued demand growth exists alongside "
            "differentiated pricing across product grades."
        )
    ],
    opportunities=[
        (
            "Growing demand may create opportunities "
            "for differentiated products."
        )
    ],
    risks=[
        (
            "Pricing variability may affect "
            "market positioning."
        )
    ],
    contradictions=[
        (
            "Low-confidence potential conflict between "
            "market growth and pricing differentiation claims."
        )
    ],
    competitive_summary=[
        "No competitive intelligence identified in this test."
    ],
    conclusion=(
        "The research supports further investigation "
        "of market segments, pricing, and competitive positioning."
    ),
)


exporter = PDFReportExporter()

pdf_path = exporter.export(
    report=report,
    output_path="reports/pdf_export_test.pdf",
)

print("\n" + "=" * 70)
print("PDF EXPORT TEST")
print("=" * 70)
print(f"\nPDF generated successfully:")
print(pdf_path)
print("\n" + "=" * 70)
print("PDF EXPORT TEST PASSED")
print("=" * 70)