# Autonomous Market & Research Intelligence Agent

An AI-powered research intelligence system that automates market research by collecting web-based evidence, analyzing information, generating actionable insights, and producing structured research reports.

**Project Status: Successfully Built | Functional Prototype Completed**

## Overview

The Autonomous Market & Research Intelligence Agent transforms a research objective into a structured, evidence-backed market intelligence report. It combines large language models, web search, evidence traceability, research metrics, and automated report generation into a unified pipeline.

The system is designed to support market research, competitor analysis, emerging trend discovery, and strategic decision-making.

## Key Features

- **AI-Powered Research:** Uses Google Gemini to support research analysis and insight generation.
- **Web Research:** Integrates Tavily Search to discover relevant online information.
- **Automated Research Pipeline:** Processes research tasks through a structured workflow.
- **Evidence Collection:** Organizes research evidence and source information.
- **Evidence Traceability:** Connects claims and insights to their supporting evidence.
- **Research Metrics:** Tracks and exports research-related metrics.
- **Insight Analysis:** Converts collected information into meaningful research insights.
- **Automated Report Generation:** Generates structured research reports.
- **PDF Export:** Exports research findings into PDF format.
- **Interactive Dashboard:** Uses Streamlit to present research metrics and results.
- **Testing:** Includes tests for pipeline execution, evidence ledgers, metrics, and PDF/report generation.

## System Architecture

Research Objective  
↓  
Research Planning  
↓  
Web Research & Evidence Collection  
↓  
Evidence Organization & Traceability  
↓  
AI-Powered Analysis & Insight Generation  
↓  
Research Metrics & Report Generation  
↓  
PDF Export & Interactive Dashboard

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core development |
| Google Gemini | LLM-powered research and analysis |
| Tavily Search | Web information discovery |
| Pydantic | Data validation and structured models |
| Streamlit | Interactive dashboard |
| JSON / Markdown | Structured data and report outputs |
| PDF Generation Tools | Exportable research reports |
| Pytest / Python Tests | Testing and validation |
| Git & GitHub | Version control and project hosting |

## Project Structure

```text
autonomous-agent-161026/
├── app/
│   ├── pipeline.py
│   ├── dashboard.py
│   ├── services/
│   │   ├── evidence_ledger.py
│   │   ├── metrics_exporter.py
│   │   ├── pdf_report_exporter.py
│   │   └── research_metrics.py
│   └── test_*.py
├── reports/
│   ├── evidence_ledger.json
│   ├── evidence_ledger.md
│   └── research_metrics.json
├── screenshots/
├── .gitignore
└── README.md
```

*The displayed structure is representative; individual files may vary.*

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/srush9356-source/autonomous-agent-161026.git
cd autonomous-agent-161026
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

If a `requirements.txt` file is present:

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Create a `.env` file in the project root and configure the required API credentials using the environment variable names expected by the application.

Required services may include Google Gemini and Tavily Search.

**Security:** Never commit `.env` files, API keys, or other confidential credentials to GitHub.

### 5. Run the application

Run the research pipeline:

```bash
python -m app.pipeline
```

Launch the Streamlit dashboard:

```bash
streamlit run app/dashboard.py
```

*Ensure dependencies and API credentials are configured before running the pipeline. Use the actual dependency list and environment variable names defined in the project.*

## Testing

The project includes tests covering key components, including:

- Research pipeline
- Evidence ledger and traceability
- Research metrics
- Downstream pipeline processing
- PDF export
- Report generation and export

Run the applicable tests using the project's configured test commands.

## Example Use Case

**Research Objective:** Analyze the Indian fruit pulp market.

The agent can support research into:

- Market trends and growth opportunities
- Competitor activities
- Pricing signals
- Export opportunities
- Evidence-backed findings for business planning

This use case demonstrates how the system can assist research and strategic analysis for businesses in the food-processing and agricultural sectors.

## Project Screenshots

Screenshots of the dashboard, research results, and generated reports can be viewed in the [`screenshots/`](screenshots/) directory.

<!-- Add screenshot previews here after confirming the actual filenames. -->

## Future Enhancements

- Advanced multi-agent orchestration
- Enhanced contradiction detection
- Deeper competitive intelligence and market gap analysis
- Improved source reliability scoring
- Expanded evaluation and confidence-calibration mechanisms
- Additional report visualizations and dashboard capabilities

## Learning Outcomes

- Building LLM-powered applications
- Integrating web search with AI workflows
- Designing evidence-backed research pipelines
- Implementing structured data validation and traceability
- Generating automated reports and dashboards
- Testing and organizing a modular Python application

## Author

**Srushti Pritam Jadhav**

GitHub: [@srush9356-source](https://github.com/srush9356-source)

---

*An AI/ML project focused on transforming web research into structured, evidence-backed market intelligence.*
