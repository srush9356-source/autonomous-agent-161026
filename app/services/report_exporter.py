from pathlib import Path

from app.models.report import ResearchReport


class ReportExporter:
    """Exports a structured research report to Markdown."""

    def export_markdown(
        self,
        report: ResearchReport,
        output_path: str = "reports/research_report.md",
    ) -> str:

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        markdown = f"""# {report.title}

## Executive Summary

{report.executive_summary}

## Key Findings

{self._bullet_list(report.key_findings)}

## Insights

{self._bullet_list(report.insights)}

## Opportunities

{self._bullet_list(report.opportunities)}

## Risks

{self._bullet_list(report.risks)}

## Contradictions

{self._bullet_list(report.contradictions)}

## Competitive Intelligence

{self._bullet_list(report.competitive_summary)}

## Conclusion

{report.conclusion}
"""

        path.write_text(markdown, encoding="utf-8")

        return str(path)

    @staticmethod
    def _bullet_list(items: list[str]) -> str:
        if not items:
            return "- None identified."

        return "\n".join(f"- {item}" for item in items)