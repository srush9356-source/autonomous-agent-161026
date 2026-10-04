from app.models.report import ResearchReport
from app.services.report_exporter import ReportExporter


report = ResearchReport(
    title="Executive Research Report: Indian Fruit Pulp Market",
    executive_summary=(
        "The Indian fruit pulp market shows increasing domestic and export "
        "demand, while differing growth estimates create some uncertainty."
    ),
    key_findings=[
        "Domestic demand for fruit pulp is increasing.",
        "Export demand for processed fruit products is increasing.",
    ],
    insights=[
        "Growing domestic and export demand may create expansion opportunities."
    ],
    risks=[
        "Different market growth estimates create uncertainty."
    ],
    opportunities=[
        "Capacity expansion.",
        "Development of export channels."
    ],
    contradictions=[
        "Available sources provide different market growth estimates."
    ],
    competitive_summary=[
        "Competitors offer processed fruit products and emphasize quality and reliable supply."
    ],
    conclusion=(
        "The market shows positive demand signals, but further research is "
        "required to reduce uncertainty around market growth estimates."
    ),
)

exporter = ReportExporter()

output_path = exporter.export_markdown(
    report=report,
    output_path="reports/test_research_report.md",
)

print(f"Report exported successfully to: {output_path}")