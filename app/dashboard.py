import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

# Add the project root to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.pipeline import ResearchPipeline
from app.models.research import ResearchObjective


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Autonomous Market & Research Intelligence",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

REPORT_PATH = REPORTS_DIR / "research_report.md"
PDF_PATH = REPORTS_DIR / "research_report.pdf"
LEDGER_JSON_PATH = REPORTS_DIR / "evidence_ledger.json"
LEDGER_MD_PATH = REPORTS_DIR / "evidence_ledger.md"
METRICS_PATH = REPORTS_DIR / "research_metrics.json"


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.7rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }

        .hero {
            padding: 1.7rem 1.8rem;
            border-radius: 18px;
            border: 1px solid rgba(128, 128, 128, 0.25);
            margin-bottom: 1.25rem;
            background: linear-gradient(
                120deg,
                rgba(55, 105, 180, 0.13),
                rgba(35, 160, 130, 0.08)
            );
        }

        .hero h1 {
            margin: 0 0 0.55rem 0;
            font-size: 2.1rem;
        }

        .hero p {
            margin: 0;
            font-size: 1rem;
            opacity: 0.85;
        }

        .small-muted {
            font-size: 0.88rem;
            opacity: 0.72;
        }

        div[data-testid="stMetric"] {
            padding: 0.8rem;
            border: 1px solid rgba(128, 128, 128, 0.22);
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_json(path: Path) -> dict[str, Any]:
    """Load JSON safely."""
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}


def load_text(path: Path) -> str:
    """Load text safely."""
    if not path.exists():
        return ""

    try:
        return path.read_text(encoding="utf-8")

    except (OSError, UnicodeDecodeError):
        try:
            return path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            return ""


def as_number(value: Any, default: float = 0.0) -> float:
    """Convert a value to a number safely."""
    try:
        result = float(value)

        if result != result:
            return default

        return result

    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int = 0) -> int:
    """Convert a value to an integer safely."""
    try:
        return int(float(value))

    except (TypeError, ValueError):
        return default


def clamp_rate(value: Any) -> float:
    """Keep percentage values between zero and one."""
    return max(
        0.0,
        min(1.0, as_number(value)),
    )


def get_ledger_counts(
    ledger: dict[str, Any],
) -> dict[str, int]:
    """Calculate counts from the evidence ledger."""

    claims = ledger.get("claims", [])
    evidence = ledger.get("evidence", [])
    insights = ledger.get("insights", [])
    sources = ledger.get("sources", [])

    return {
        "claims": len(claims) if isinstance(claims, list) else 0,
        "evidence": len(evidence) if isinstance(evidence, list) else 0,
        "insights": len(insights) if isinstance(insights, list) else 0,
        "sources": len(sources) if isinstance(sources, list) else 0,
    }


def get_metric(
    metrics: dict[str, Any],
    key: str,
    fallback: Any = 0,
) -> Any:
    """Get a metric without treating zero as missing."""

    value = metrics.get(key, fallback)

    return fallback if value is None else value


def confidence_label(value: Any) -> str:
    """Convert confidence into a readable label."""

    score = as_number(value)

    if score >= 0.80:
        return "High"

    if score >= 0.55:
        return "Medium"

    return "Low"


def render_rate(label: str, value: Any) -> None:
    """Display a percentage and progress bar."""

    rate = clamp_rate(value)

    st.write(f"**{label}:** {rate:.0%}")
    st.progress(rate)


def download_if_exists(
    label: str,
    path: Path,
    mime: str,
    filename: str,
    key: str,
) -> None:
    """Enable a download only when the file exists."""

    if path.exists():

        try:
            data = path.read_bytes()

            st.download_button(
                label=label,
                data=data,
                file_name=filename,
                mime=mime,
                key=key,
                use_container_width=True,
            )

        except OSError:
            st.caption(f"Could not read {filename}.")

    else:
        st.button(
            label,
            disabled=True,
            key=f"{key}_disabled",
            use_container_width=True,
            help=f"{filename} is not available yet.",
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🔎 Research Intelligence")

    st.caption(
        "Autonomous, evidence-backed market research"
    )

    if st.button(
        "🔄 Refresh dashboard",
        use_container_width=True,
    ):
        st.rerun()

    st.divider()

    st.markdown("### Pipeline Files")

    report_exists = REPORT_PATH.exists()
    ledger_exists = LEDGER_JSON_PATH.exists()
    metrics_exists = METRICS_PATH.exists()
    pdf_exists = PDF_PATH.exists()

    if report_exists:
        st.success("Executive Report Ready")
    else:
        st.info("Executive Report Pending")

    if ledger_exists:
        st.success("Evidence Ledger Ready")
    else:
        st.warning("Evidence Ledger Pending")

    if metrics_exists:
        st.success("Research Metrics Ready")
    else:
        st.info("Research Metrics Pending")

    if pdf_exists:
        st.success("PDF Export Ready")
    else:
        st.info("PDF Export Pending")

    st.divider()

    st.caption(
        "Live research requires configured API keys. "
        "Provider quotas, network issues, and inaccessible "
        "websites can affect results."
    )


# ============================================================
# HERO SECTION
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>🔎 Autonomous Market &amp; Research Intelligence</h1>

        <p>
            Transform a research question into a structured,
            evidence-backed report with source traceability,
            market insights, and research quality metrics.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### 🎯 Start a Research Project")

st.write(
    "Research any business, company, industry, product, "
    "technology, competitor, or market. Your research topic "
    "is supplied dynamically; it is not restricted to one industry."
)


# ============================================================
# RESEARCH INPUT FORM
# ============================================================

with st.form(
    "research_form",
    clear_on_submit=False,
):

    topic = st.text_input(
        "Research Topic *",
        value="",
        placeholder="Example: Electric Vehicle Market in India",
        help=(
            "You can research any topic, industry, product, "
            "company, or business opportunity."
        ),
    )

    industry = st.text_input(
        "Industry or Business Area (Optional)",
        value="",
        placeholder="Example: Automotive, Agriculture, Healthcare, AI",
    )

    objective = st.text_area(
        "Research Objective *",
        value="",
        placeholder=(
            "Describe what you want to investigate. For example, "
            "analyze market trends, competitors, pricing, growth "
            "opportunities, risks, and supporting evidence."
        ),
        height=120,
    )

    mode_label = st.radio(
        "Research Depth",
        options=[
            "FAST — Quota-Safe Research",
            "FULL — Comprehensive Intelligence",
        ],
        horizontal=True,
        help=(
            "FAST is intended for a smaller research run. "
            "FULL requests more comprehensive research and "
            "may consume more API quota."
        ),
    )

    submitted = st.form_submit_button(
        "🚀 Start Autonomous Research",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# EXECUTE RESEARCH
# ============================================================

if submitted:

    clean_topic = topic.strip()
    clean_objective = objective.strip()

    if not clean_topic:

        st.error("Please enter a research topic.")

    elif not clean_objective:

        st.error("Please enter a research objective.")

    else:

        selected_mode = (
            "FAST"
            if mode_label.startswith("FAST")
            else "FULL"
        )

        try:

            with st.spinner(
                f"Researching '{clean_topic}' in "
                f"{selected_mode} mode. Please wait..."
            ):

                pipeline = ResearchPipeline()

                result = pipeline.run(
                    research_objective=ResearchObjective(
                        topic=clean_topic,
                        industry=industry.strip() or None,
                        objective=clean_objective,
                    ),
                    mode=selected_mode,
                )

            st.success("Research pipeline finished.")

            if result is not None:

                with st.expander(
                    "View Pipeline Result",
                    expanded=False,
                ):

                    if isinstance(result, (dict, list)):
                        st.json(result)
                    else:
                        st.write(result)

            st.rerun()

        except Exception as exc:

            st.error(
                "The research run could not be completed."
            )

            st.exception(exc)

            st.info(
                "Check your API keys, provider quota, network "
                "connection, and terminal logs. Existing outputs "
                "may be affected if the pipeline overwrites them."
            )


# ============================================================
# LOAD SAVED RESEARCH OUTPUTS
# ============================================================

ledger = load_json(LEDGER_JSON_PATH)
saved_metrics = load_json(METRICS_PATH)

report = load_text(REPORT_PATH)
ledger_markdown = load_text(LEDGER_MD_PATH)

ledger_counts = get_ledger_counts(ledger)


# ============================================================
# METRICS
# ============================================================

sources_count = as_int(
    get_metric(
        saved_metrics,
        "sources_analyzed",
        ledger_counts["sources"],
    )
)

evidence_count = as_int(
    get_metric(
        saved_metrics,
        "evidence_records",
        ledger_counts["evidence"],
    )
)

claims_count = as_int(
    get_metric(
        saved_metrics,
        "claims_generated",
        ledger_counts["claims"],
    )
)

insights_count = as_int(
    get_metric(
        saved_metrics,
        "insights_generated",
        ledger_counts["insights"],
    )
)

traceability_rate = clamp_rate(
    get_metric(
        saved_metrics,
        "evidence_traceability_rate",
        0.0,
    )
)

claim_support_rate = clamp_rate(
    get_metric(
        saved_metrics,
        "claim_support_rate",
        0.0,
    )
)

overall_quality = clamp_rate(
    get_metric(
        saved_metrics,
        "overall_research_quality",
        0.0,
    )
)

extraction_success_rate = clamp_rate(
    get_metric(
        saved_metrics,
        "extraction_success_rate",
        0.0,
    )
)

average_claim_confidence = as_number(
    get_metric(
        saved_metrics,
        "average_claim_confidence",
        0.0,
    )
)

average_evidence_confidence = as_number(
    get_metric(
        saved_metrics,
        "average_evidence_confidence",
        0.0,
    )
)

contradictions = as_int(
    get_metric(
        saved_metrics,
        "contradictions_detected",
        0,
    )
)

high_quality_sources = as_int(
    get_metric(
        saved_metrics,
        "high_quality_sources",
        0,
    )
)

extracted_sources = as_int(
    get_metric(
        saved_metrics,
        "sources_successfully_extracted",
        0,
    )
)


# ============================================================
# RESEARCH OVERVIEW
# ============================================================

st.divider()

st.markdown("## 📊 Research Overview")

if not ledger and not saved_metrics and not report:

    st.info(
        "No saved research results were found. "
        "Start a research project above to populate the dashboard."
    )

else:

    st.caption(
        "Metrics are read from saved pipeline outputs. "
        "Missing values are shown as zero rather than estimated."
    )


metric_cols = st.columns(4)

metric_cols[0].metric(
    "Sources Discovered",
    f"{sources_count:,}",
)

metric_cols[1].metric(
    "Evidence Records",
    f"{evidence_count:,}",
)

metric_cols[2].metric(
    "Claims Generated",
    f"{claims_count:,}",
)

metric_cols[3].metric(
    "Insights Generated",
    f"{insights_count:,}",
)


quality_cols = st.columns(3)

quality_cols[0].metric(
    "Overall Research Quality",
    f"{overall_quality:.0%}",
)

quality_cols[1].metric(
    "Evidence Traceability",
    f"{traceability_rate:.0%}",
)

quality_cols[2].metric(
    "Claim Support Rate",
    f"{claim_support_rate:.0%}",
)


# ============================================================
# DASHBOARD TABS
# ============================================================

overview_tab, report_tab, evidence_tab, insights_tab, export_tab = (
    st.tabs(
        [
            "📌 Quality & Coverage",
            "📄 Executive Report",
            "🔗 Evidence Traceability",
            "💡 Insights",
            "📦 Exports & Architecture",
        ]
    )
)


# ============================================================
# TAB 1: QUALITY AND COVERAGE
# ============================================================

with overview_tab:

    st.subheader("📊 Research Coverage")

    coverage_left, coverage_right = st.columns(2)

    with coverage_left:

        st.markdown("#### Source Extraction")

        st.metric(
            "Sources Successfully Extracted",
            f"{extracted_sources:,}",
        )

        render_rate(
            "Extraction Success Rate",
            extraction_success_rate,
        )

        st.markdown("#### Source Quality")

        st.metric(
            "High-Quality Sources",
            f"{high_quality_sources:,}",
        )

    with coverage_right:

        st.markdown("#### Research Quality")

        render_rate(
            "Overall Research Quality",
            overall_quality,
        )

        render_rate(
            "Evidence Traceability",
            traceability_rate,
        )

        render_rate(
            "Claim Support Rate",
            claim_support_rate,
        )

    st.markdown("#### Confidence & Consistency")

    confidence_cols = st.columns(3)

    confidence_cols[0].metric(
        "Average Claim Confidence",
        f"{average_claim_confidence:.0%}",
    )

    confidence_cols[1].metric(
        "Average Evidence Confidence",
        f"{average_evidence_confidence:.0%}",
    )

    confidence_cols[2].metric(
        "Contradictions Detected",
        f"{contradictions:,}",
    )

    with st.expander("View Raw Saved Metrics"):

        if saved_metrics:
            st.json(saved_metrics)
        else:
            st.info(
                "The research metrics JSON file is not available."
            )


# ============================================================
# TAB 2: EXECUTIVE REPORT
# ============================================================

with report_tab:

    st.subheader("📄 Executive Research Report")

    if report.strip():

        st.markdown(report)

    else:

        st.info(
            "No executive report is available yet. "
            "Run a research project to generate one."
        )


# ============================================================
# TAB 3: EVIDENCE TRACEABILITY
# ============================================================

with evidence_tab:

    st.subheader("🔗 Claim → Evidence → Source")

    claims = ledger.get("claims", [])

    if not isinstance(claims, list):
        claims = []

    if claims:

        st.caption(
            "Expand a claim to inspect its linked evidence "
            "and source information."
        )

        for index, claim in enumerate(claims, start=1):

            if not isinstance(claim, dict):
                continue

            claim_id = claim.get(
                "claim_id",
                f"claim_{index}",
            )

            claim_text = claim.get(
                "claim",
                "Claim text unavailable",
            )

            confidence = as_number(
                claim.get("claim_confidence", 0.0)
            )

            status = claim.get(
                "status",
                "Unknown",
            )

            linked_evidence = claim.get(
                "evidence",
                [],
            )

            if not isinstance(linked_evidence, list):
                linked_evidence = []

            with st.expander(
                f"{claim_id} · "
                f"{confidence_label(confidence)} confidence · "
                f"{status}"
            ):

                st.write(claim_text)

                st.caption(
                    f"Claim Confidence: {confidence:.0%}"
                )

                if not linked_evidence:

                    st.warning(
                        "No linked evidence was recorded for this claim."
                    )

                    continue

                for evidence_index, item in enumerate(
                    linked_evidence,
                    start=1,
                ):

                    if not isinstance(item, dict):

                        st.write(item)
                        continue

                    st.markdown(
                        f"**Evidence {evidence_index}**"
                    )

                    evidence_text = item.get(
                        "supporting_text",
                        item.get(
                            "claim_from_source",
                            "Evidence text unavailable",
                        ),
                    )

                    st.write(evidence_text)

                    evidence_id = item.get(
                        "evidence_id",
                        "N/A",
                    )

                    source_type = item.get(
                        "source_type",
                        "Unknown",
                    )

                    evidence_confidence = as_number(
                        item.get(
                            "evidence_confidence",
                            0.0,
                        )
                    )

                    st.caption(
                        f"Evidence ID: {evidence_id} · "
                        f"Type: {source_type} · "
                        f"Confidence: {evidence_confidence:.0%}"
                    )

                    source_title = item.get(
                        "source_title",
                        "Untitled source",
                    )

                    st.write(
                        f"**Source:** {source_title}"
                    )

                    source_url = item.get("source_url")

                    if (
                        isinstance(source_url, str)
                        and source_url.startswith(
                            ("https://", "http://")
                        )
                    ):

                        st.link_button(
                            "Open Source",
                            source_url,
                            key=(
                                f"source_link_"
                                f"{index}_{evidence_index}"
                            ),
                        )

                    if evidence_index < len(linked_evidence):
                        st.divider()

    else:

        st.info(
            "No claim records were found in the evidence ledger. "
            "The ledger may be missing or may use a different schema."
        )

    with st.expander("View Evidence Ledger JSON"):

        if ledger:
            st.json(ledger)
        else:
            st.info(
                "The evidence ledger JSON file is not available."
            )

    if ledger_markdown.strip():

        with st.expander("View Evidence Ledger Markdown"):

            st.markdown(ledger_markdown)


# ============================================================
# TAB 4: INSIGHTS
# ============================================================

with insights_tab:

    st.subheader("💡 Insight Traceability")

    insights = ledger.get("insights", [])

    if not isinstance(insights, list):
        insights = []

    if insights:

        for index, insight in enumerate(
            insights,
            start=1,
        ):

            if not isinstance(insight, dict):
                continue

            insight_id = insight.get(
                "insight_id",
                f"insight_{index}",
            )

            title = insight.get(
                "title",
                f"Insight {index}",
            )

            confidence = as_number(
                insight.get("confidence", 0.0)
            )

            supporting_claims = insight.get(
                "supporting_claims",
                [],
            )

            if not isinstance(supporting_claims, list):
                supporting_claims = []

            with st.expander(
                f"{insight_id} · {title} · "
                f"{confidence_label(confidence)} confidence"
            ):

                st.write(
                    insight.get(
                        "description",
                        insight.get("insight", title),
                    )
                )

                st.caption(
                    f"Insight Confidence: {confidence:.0%}"
                )

                if supporting_claims:

                    st.markdown(
                        "**Supporting Claims & Evidence**"
                    )

                    for claim_index, supporting_claim in enumerate(
                        supporting_claims,
                        start=1,
                    ):

                        if isinstance(supporting_claim, dict):

                            supporting_claim_id = supporting_claim.get(
                                "claim_id",
                                f"Claim {claim_index}",
                            )

                            st.markdown(
                                f"**{supporting_claim_id}**"
                            )

                            st.write(
                                supporting_claim.get(
                                    "claim",
                                    supporting_claim.get(
                                        "text",
                                        "Claim text unavailable",
                                    ),
                                )
                            )

                            evidence_items = supporting_claim.get(
                                "evidence",
                                [],
                            )

                            if isinstance(evidence_items, list):

                                for evidence in evidence_items:

                                    if isinstance(evidence, dict):

                                        st.caption(
                                            "Evidence: "
                                            f"{evidence.get('evidence_id', 'N/A')} · "
                                            f"{evidence.get('source_title', 'Untitled source')}"
                                        )

                        else:

                            st.write(supporting_claim)

                else:

                    st.caption(
                        "No supporting claims are attached to this insight."
                    )

    else:

        st.info(
            "No insight records were found in the evidence ledger."
        )


# ============================================================
# TAB 5: EXPORTS AND ARCHITECTURE
# ============================================================

with export_tab:

    st.subheader("📦 Export Research Outputs")

    st.write(
        "Download the files produced by your pipeline. "
        "Downloads are enabled only when the corresponding files exist."
    )

    download_col1, download_col2, download_col3 = st.columns(3)

    with download_col1:

        download_if_exists(
            label="⬇️ Download Report (Markdown)",
            path=REPORT_PATH,
            mime="text/markdown",
            filename="research_report.md",
            key="download_report_md",
        )

    with download_col2:

        download_if_exists(
            label="⬇️ Download Report (PDF)",
            path=PDF_PATH,
            mime="application/pdf",
            filename="research_report.pdf",
            key="download_report_pdf",
        )

    with download_col3:

        download_if_exists(
            label="⬇️ Download Evidence Ledger (JSON)",
            path=LEDGER_JSON_PATH,
            mime="application/json",
            filename="evidence_ledger.json",
            key="download_ledger_json",
        )

    if ledger_markdown.strip():

        st.download_button(
            "⬇️ Download Evidence Ledger (Markdown)",
            data=ledger_markdown.encode("utf-8"),
            file_name="evidence_ledger.md",
            mime="text/markdown",
            key="download_ledger_md",
        )

    st.divider()

    st.subheader("🏗️ System Architecture")

    with st.expander("View Research Workflow"):

        st.markdown(
            """
            1. **Research Objective** — accepts the topic, industry, and question.
            2. **Research Planning** — the pipeline creates research tasks.
            3. **Source Discovery** — searches for potentially relevant sources.
            4. **Evidence Extraction** — extracts information from accessible pages.
            5. **Claim and Insight Generation** — organizes collected findings.
            6. **Quality and Traceability** — reports metrics produced by the pipeline.
            7. **Report Generation** — saves the executive report and evidence ledger.
            8. **Export** — provides available Markdown, PDF, and JSON files.

            Actual stages and outputs depend on your pipeline implementation,
            configured providers, API quotas, and accessible sources.
            """
        )

    with st.expander("Show Output File Locations"):

        for path in (
            REPORT_PATH,
            PDF_PATH,
            LEDGER_JSON_PATH,
            LEDGER_MD_PATH,
            METRICS_PATH,
        ):

            st.code(str(path), language=None)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <p class="small-muted">
        Autonomous Market &amp; Research Intelligence ·
        Evidence-backed research with claim-to-source traceability
    </p>
    """,
    unsafe_allow_html=True,
)