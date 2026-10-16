from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    ListFlowable,
    ListItem,
)


class PDFReportExporter:
    """Exports the research report as a professional PDF."""

    def __init__(self):
        self.styles = getSampleStyleSheet()

        self.title_style = ParagraphStyle(
            "ReportTitle",
            parent=self.styles["Title"],
            alignment=TA_CENTER,
            fontSize=22,
            leading=28,
            spaceAfter=18,
        )

        self.subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=self.styles["Normal"],
            alignment=TA_CENTER,
            fontSize=11,
            leading=16,
            spaceAfter=24,
        )

        self.heading_style = ParagraphStyle(
            "SectionHeading",
            parent=self.styles["Heading1"],
            fontSize=16,
            leading=20,
            spaceBefore=14,
            spaceAfter=10,
        )

        self.body_style = ParagraphStyle(
            "Body",
            parent=self.styles["BodyText"],
            fontSize=10,
            leading=15,
            spaceAfter=8,
        )

        self.bullet_style = ParagraphStyle(
            "Bullet",
            parent=self.body_style,
            leftIndent=14,
            firstLineIndent=0,
            spaceAfter=5,
        )

    def _safe_text(self, value) -> str:
        if value is None:
            return ""

        text = str(value)

        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def _add_bullets(
        self,
        story,
        items,
    ):
        if not items:
            story.append(
                Paragraph(
                    "No information available.",
                    self.body_style,
                )
            )
            return

        list_items = []

        for item in items:
            list_items.append(
                ListItem(
                    Paragraph(
                        self._safe_text(item),
                        self.bullet_style,
                    ),
                    leftIndent=12,
                )
            )

        story.append(
            ListFlowable(
                list_items,
                bulletType="bullet",
                start="circle",
                leftIndent=18,
            )
        )

        story.append(Spacer(1, 8))

    def export(
        self,
        report,
        output_path: str = (
            "reports/research_report.pdf"
        ),
    ) -> str:

        path = Path(output_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = SimpleDocTemplate(
            str(path),
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title=report.title,
            author=(
                "Autonomous Market & "
                "Research Intelligence Agent"
            ),
        )

        story = []

        # -----------------------------------------------------
        # TITLE
        # -----------------------------------------------------

        story.append(
            Paragraph(
                self._safe_text(report.title),
                self.title_style,
            )
        )

        story.append(
            Paragraph(
                "Autonomous Market & Research "
                "Intelligence Agent",
                self.subtitle_style,
            )
        )

        # -----------------------------------------------------
        # EXECUTIVE SUMMARY
        # -----------------------------------------------------

        story.append(
            Paragraph(
                "Executive Summary",
                self.heading_style,
            )
        )

        story.append(
            Paragraph(
                self._safe_text(
                    report.executive_summary
                ),
                self.body_style,
            )
        )

        # -----------------------------------------------------
        # KEY FINDINGS
        # -----------------------------------------------------

        story.append(
            Paragraph(
                "Key Findings",
                self.heading_style,
            )
        )

        self._add_bullets(
            story,
            report.key_findings,
        )

        # -----------------------------------------------------
        # INSIGHTS
        # -----------------------------------------------------

        story.append(
            Paragraph(
                "Strategic Insights",
                self.heading_style,
            )
        )

        self._add_bullets(
            story,
            report.insights,
        )

        # -----------------------------------------------------
        # OPPORTUNITIES
        # -----------------------------------------------------

        story.append(
            Paragraph(
                "Opportunities",
                self.heading_style,
            )
        )

        self._add_bullets(
            story,
            report.opportunities,
        )

        # -----------------------------------------------------
        # RISKS
        # -----------------------------------------------------

        story.append(
            Paragraph(
                "Risks",
                self.heading_style,
            )
        )

        self._add_bullets(
            story,
            report.risks,
        )

        # -----------------------------------------------------
        # CONTRADICTIONS
        # -----------------------------------------------------

        story.append(
            Paragraph(
                "Detected Contradictions",
                self.heading_style,
            )
        )

        self._add_bullets(
            story,
            report.contradictions,
        )

        # -----------------------------------------------------
        # COMPETITIVE INTELLIGENCE
        # -----------------------------------------------------

        story.append(
            Paragraph(
                "Competitive Intelligence",
                self.heading_style,
            )
        )

        self._add_bullets(
            story,
            report.competitive_summary,
        )

        # -----------------------------------------------------
        # CONCLUSION
        # -----------------------------------------------------

        story.append(
            Paragraph(
                "Conclusion",
                self.heading_style,
            )
        )

        story.append(
            Paragraph(
                self._safe_text(
                    report.conclusion
                ),
                self.body_style,
            )
        )

        document.build(story)

        return str(path)