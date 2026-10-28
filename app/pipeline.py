import json
from pathlib import Path
from datetime import datetime, timezone
from app.agents.planner import ResearchPlanner
from app.models.research import ResearchObjective
from app.models.evidence import Evidence
from app.models.claim import Claim
from app.services.source_validator import SourceValidator
from app.services.source_scorer import SourceScorer
from app.services.evidence_ledger import EvidenceLedger
from app.services.research_metrics import ResearchMetrics
from app.tools.search import WebSearchTool
from app.tools.web_extractor import WebContentExtractor
from app.services.evidence_extractor import EvidenceExtractor
from app.services.claim_extractor import ClaimExtractor
from app.services.contradiction_detector import ContradictionDetector
from app.services.insight_analyzer import InsightAnalyzer
from app.models.insight import Insight
from app.services.competitive_intelligence import (
    CompetitiveIntelligenceExtractor,
)
from app.services.report_generator import ReportGenerator
from app.services.report_exporter import ReportExporter
from app.services.pdf_report_exporter import PDFReportExporter
from app.services.metrics_exporter import MetricsExporter


class ResearchPipeline:
    """End-to-end autonomous market research pipeline."""
    CHECKPOINT_DIR = Path("reports/checkpoints")
    def _load_checkpoint(self, name, run_signature):
        """Load a checkpoint only if it belongs to the current run."""
        path = self.CHECKPOINT_DIR / f"{name}.json"

        if not path.exists():
            return None

        try:
            with path.open("r", encoding="utf-8") as file:
                checkpoint = json.load(file)

            if checkpoint.get("run_signature") != run_signature:
                return None

            print(f"Reusing checkpoint: {name}")
            return checkpoint.get("data")

        except (json.JSONDecodeError, OSError):
            print(f"Skipping invalid checkpoint: {name}")
            return None

    def _save_checkpoint(self, name, data):
        """Save a pipeline checkpoint without overwriting other artifacts."""
        self.CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

        path = self.CHECKPOINT_DIR / f"{name}.json"
        temporary_path = path.with_suffix(".tmp")

        payload = {
            "checkpoint": name,
            "run_signature": self._current_run_signature,
            "saved_at_utc": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }

        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(
                payload,
                file,
                ensure_ascii=False,
                indent=2,
                default=lambda value: (
                    value.model_dump(mode="json")
                    if hasattr(value, "model_dump")
                    else value.__dict__
                    if hasattr(value, "__dict__")
                    else str(value)
                ),
            )

        temporary_path.replace(path)
        print(f"Checkpoint saved: {path}")

    def _mark_stage(self, stage, status, details=None):
        """Record whether a pipeline stage completed or failed."""
        path = self.CHECKPOINT_DIR / "pipeline_status.json"
        self.CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as file:
                    status_data = json.load(file)
            except (json.JSONDecodeError, OSError):
                status_data = {"stages": {}}
        else:
            status_data = {"stages": {}}

        status_data["stages"][stage] = {
            "status": status,
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "details": details,
        }

        temporary_path = path.with_suffix(".tmp")

        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(
                status_data,
                file,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

        temporary_path.replace(path)
    def __init__(self):
        self.planner = ResearchPlanner()
        self.search_tool = WebSearchTool()
        self.source_validator = SourceValidator()
        self.source_scorer = SourceScorer()
        self.web_extractor = WebContentExtractor()
        self.evidence_extractor = EvidenceExtractor()
        self.claim_extractor = ClaimExtractor()
        self.contradiction_detector = ContradictionDetector()
        self.insight_analyzer = InsightAnalyzer()
        self.competitive_intelligence = CompetitiveIntelligenceExtractor()
        self.evidence_ledger = EvidenceLedger()
        self.research_metrics = ResearchMetrics()
        self.report_generator = ReportGenerator()
        self.report_exporter = ReportExporter()
        self.pdf_report_exporter = PDFReportExporter()
        self.metrics_exporter = MetricsExporter()

    def run(
        self,
        research_objective: ResearchObjective,
        mode: str = "FULL",
    ):
        """
        Run the research pipeline.

        FAST mode:
            Uses up to 3 research tasks, 2 results per task,
            and up to 2 sources for competitive intelligence.

        FULL mode:
            Uses all planned tasks and up to 5 results per task.

        Returns:
            Dictionary containing report paths and research metrics.
        """

        mode = mode.upper().strip()
        self._current_run_signature = json.dumps(
            {
                "topic": research_objective.topic.strip().lower(),
                "objective": research_objective.objective.strip().lower(),
                "industry": (
                    research_objective.industry.strip().lower()
                    if research_objective.industry
                    else None
                ),
                "mode": mode,
            },
            sort_keys=True,
        )

        if mode not in {"FAST", "FULL"}:
            raise ValueError(
                "Invalid mode. Choose 'FAST' or 'FULL'."
            )

        print("\n" + "=" * 70)
        print("AUTONOMOUS MARKET & RESEARCH INTELLIGENCE AGENT")
        print("=" * 70)
        print(f"Mode: {mode}")
        print(f"Research topic: {research_objective.topic}")

        # ---------------------------------------------------------
        # 1. RESEARCH PLANNING
        # ---------------------------------------------------------
        print("\n[1/10] Creating research plan...")

        tasks = self.planner.create_plan(research_objective)

        if not tasks:
            raise RuntimeError(
                "Research planner returned no tasks."
            )

        selected_tasks = tasks[:3] if mode == "FAST" else tasks

        print(f"Planned tasks: {len(tasks)}")
        print(f"Tasks selected: {len(selected_tasks)}")

        # ---------------------------------------------------------
        # 2. LIVE WEB RESEARCH
        # ---------------------------------------------------------
        print("\n[2/10] Performing web research...")

        all_sources = []
        failed_research_tasks = 0
        failed_evidence_batches = 0

        max_results = 2 if mode == "FAST" else 5

        for task_number, task in enumerate(
            selected_tasks,
            start=1,
        ):
            print(
                f"\nResearch task {task_number}/"
                f"{len(selected_tasks)}: {task.question}"
            )

            try:
                search_results = self.search_tool.search(
                    query=task.question,
                    max_results=max_results,
                )

                print(
                    f"Search results: {len(search_results)}"
                )

                validated_sources = (
                    self.source_validator.validate(
                        search_results
                    )
                )

                for source in validated_sources:
                    try:
                        scored_source = self.source_scorer.score(
                            source
                        )
                        all_sources.append(scored_source)

                    except Exception as exc:
                        print(
                            f"Source scoring failed for "
                            f"{getattr(source, 'url', 'unknown URL')}: "
                            f"{exc}"
                        )

            except Exception as exc:
                failed_research_tasks += 1
                print(f"Research task failed: {exc}")

        # Deduplicate sources by URL.
        unique_sources = {}

        for source in all_sources:
            if getattr(source, "url", None):
                unique_sources[source.url] = source

        all_sources = list(unique_sources.values())

        print(f"\nUnique sources collected: {len(all_sources)}")

        if not all_sources:
            raise RuntimeError(
                "No usable sources were collected. "
                "Check search configuration, API credentials, "
                "network access, and source validation."
            )

        # ---------------------------------------------------------
        # 3. WEB CONTENT EXTRACTION
        # ---------------------------------------------------------
            print("\n[3/10] Extracting webpage content...")

        source_contents = []
        extracted_sources = []

        saved_content = self._load_checkpoint(
            "source_contents",
            self._current_run_signature,
        )

        if saved_content:
            sources_by_url = {
                source.url: source
                for source in all_sources
                if getattr(source, "url", None)
            }

            for item in saved_content:
                source = sources_by_url.get(item.get("url"))
                content = item.get("content", "")

                if source and content:
                    source_contents.append((source, content))
                    extracted_sources.append(source)

            print(
                f"Recovered {len(source_contents)} "
                "webpages from checkpoint."
            )

        if not source_contents:
            for index, source in enumerate(all_sources, start=1):
                print(
                    f"\nExtracting source {index}/{len(all_sources)}"
                )
                print(source.url)

                try:
                    content = self.web_extractor.extract(source.url)

                    if not content or not str(content).strip():
                        print("Skipped: webpage returned empty content.")
                        continue

                    source_contents.append((source, content))
                    extracted_sources.append(source)

                    print(f"Extracted {len(content)} characters.")

                except Exception as exc:
                    print(f"Web extraction failed for {source.url}: {exc}")

            self._save_checkpoint(
                "source_contents",
                [
                    {"url": source.url, "content": content}
                    for source, content in source_contents
                ],
            )

        print(f"\nSuccessfully extracted webpages: {len(source_contents)}")

        self._mark_stage(
            "web_content_extraction",
            "completed",
            {"extracted_sources": len(source_contents)},
        )

        if not source_contents:
            raise RuntimeError(
                "No webpage content could be extracted."
            )

        # ---------------------------------------------------------
        # 4. EVIDENCE EXTRACTION
        # ---------------------------------------------------------
        print("\n[4/10] Extracting evidence...")

        evidence_records = self._load_checkpoint(
            "evidence",
            self._current_run_signature,
        )
        if evidence_records:
            evidence_records = [
                Evidence.model_validate(item)
                if isinstance(item, dict)
                else item
                for item in evidence_records
            ]

        if evidence_records:
            print(
                f"Recovered {len(evidence_records)} "
                "evidence records from checkpoint."
            )
        else:
            evidence_records = []
            batch_size = 3

            for batch_start in range(
                0,
                len(source_contents),
                batch_size,
            ):
                batch = source_contents[
                    batch_start:batch_start + batch_size
                ]

                batch_number = batch_start // batch_size + 1

                print(
                    f"\nEvidence batch {batch_number}: "
                    f"{len(batch)} sources"
                )

                try:
                    batch_evidence = (
                        self.evidence_extractor.extract_batch(batch)
                    )

                    if batch_evidence:
                        for evidence in batch_evidence:
                            evidence.evidence_id = (
                                f"EVD-{len(evidence_records) + 1:03d}"
                            )
                            evidence_records.append(evidence)

                    print(
                        f"Evidence records generated: "
                        f"{len(batch_evidence or [])}"
                    )

                except Exception as exc:
                    failed_evidence_batches += 1
                    print(f"Evidence batch failed: {exc}")

            self._save_checkpoint("evidence", evidence_records)

        print(f"\nTotal evidence records: {len(evidence_records)}")

        self._mark_stage(
            "evidence_extraction",
            "completed" if evidence_records else "failed",
            {"evidence_records": len(evidence_records)},
        )

        if not evidence_records:
            raise RuntimeError(
                "No evidence records were generated. "
                "Check the evidence extractor and LLM configuration."
            )

        # ---------------------------------------------------------
        # 5. CLAIM EXTRACTION
        # ---------------------------------------------------------
        print("\n[5/10] Extracting research claims...")

        claims = self._load_checkpoint(
            "claims",
            self._current_run_signature,
        )
        if claims:
            claims = [
                Claim.model_validate(item)
                if isinstance(item, dict)
                else item
                for item in claims
            ]

        if claims:
            print(f"Recovered {len(claims)} claims from checkpoint.")
        else:
            claims = self.claim_extractor.extract(evidence_records)

            print(f"Claims generated: {len(claims)}")
            self._save_checkpoint("claims", claims)

        self._mark_stage(
            "claim_extraction",
            "completed" if claims else "failed",
            {"claims": len(claims)},
        )

        if not claims:
            raise RuntimeError(
                "No research claims were generated."
            )

        # ---------------------------------------------------------
        
        # ---------------------------------------------------------
        # 6. CONTRADICTION DETECTION
        # ---------------------------------------------------------
        print("\n[6/10] Detecting contradictions...")

        contradictions = self._load_checkpoint(
            "contradictions",
            self._current_run_signature,
        )

        contradiction_status = "failed"

        if contradictions is not None:
            contradiction_status = "completed"
            print(
                f"Recovered {len(contradictions)} contradictions "
                "from checkpoint."
            )
        else:
            contradictions = []

            try:
                contradictions = self.contradiction_detector.detect(
                    claims
                )

                contradiction_status = getattr(
                    self.contradiction_detector,
                    "last_status",
                    "unverified",
                )

                if contradiction_status == "completed":
                    self._save_checkpoint(
                        "contradictions",
                        contradictions,
                    )
                else:
                    print(
                        "WARNING: Contradiction detection was not "
                        "confirmed as successful."
                    )

            except Exception as exc:
                contradiction_status = "failed"
                print(f"Contradiction detection failed: {exc}")

        self._mark_stage(
            "contradiction_detection",
            contradiction_status,
            {
                "contradictions": len(contradictions),
                "verification_confirmed": (
                    contradiction_status == "completed"
                ),
            },
        )

        print(
            f"Contradictions detected: {len(contradictions)}"
        )

        # ---------------------------------------------------------
        # 7. INSIGHT ANALYSIS
        # ---------------------------------------------------------
        print("\n[7/10] Analyzing research insights...")

        insights = self._load_checkpoint(
            "insights",
            self._current_run_signature,
        )

        if insights:
            insights = [
                item if isinstance(item, Insight)
                else Insight.model_validate(item)
                for item in insights
            ]
            print(f"Recovered {len(insights)} insights from checkpoint.")
        else:
            insights = self.insight_analyzer.analyze(claims, contradictions)
            print(f"Insights generated: {len(insights)}")
            self._save_checkpoint("insights", insights)

        self._mark_stage(
            "insight_analysis",
            "completed" if insights else "failed",
            {"insights": len(insights)},
        )

        # ---------------------------------------------------------
        # 8. EVIDENCE LEDGER
        # ---------------------------------------------------------
        print("\n[8/10] Building evidence ledger...")

        ledger = self.evidence_ledger.build(
            evidence_records=evidence_records,
            claims=claims,
            insights=insights,
        )

        insight_traceability = (
            self.evidence_ledger.add_insight_traceability(
                ledger=ledger,
                insights=insights,
            )
        )

        ledger_json_path = (
            self.evidence_ledger.export_json(
                ledger=ledger,
                insights=insight_traceability,
                output_path="reports/evidence_ledger.json",
            )
        )

        ledger_markdown_path = (
            self.evidence_ledger.export_markdown(
                ledger=ledger,
                insights=insight_traceability,
                output_path="reports/evidence_ledger.md",
            )
        )

        print(f"Evidence ledger JSON: {ledger_json_path}")
        print(f"Evidence ledger Markdown: {ledger_markdown_path}")

        # ---------------------------------------------------------
        # 9. RESEARCH METRICS AND COMPETITIVE INTELLIGENCE
        # ---------------------------------------------------------
        print("\n[9/10] Calculating research metrics...")

        metrics = self.research_metrics.calculate(
            sources=all_sources,
            extracted_sources=extracted_sources,
            evidence=evidence_records,
            claims=claims,
            contradictions=contradictions,
            insights=insights,
        )
        metrics["pipeline_status"] = (
            "completed_with_warnings"
            if (
                failed_research_tasks > 0
                or failed_evidence_batches > 0
                or contradiction_status != "completed"
            )
            else "completed"
        )

        metrics["contradiction_detection_status"] = (
            contradiction_status
        )

        metrics["failed_research_tasks"] = (
            failed_research_tasks
        )

        metrics["failed_evidence_batches"] = (
            failed_evidence_batches
        )

        metrics_path = self.metrics_exporter.export(
            metrics=metrics,
            output_path="reports/research_metrics.json",
        )

        print(f"Research metrics saved: {metrics_path}")

        for key, value in metrics.items():
            print(f"  {key}: {value}")

        # Extract competitive intelligence from webpage content.
        competitive_intelligence = []

        competitive_sources = (
            source_contents[:2]
            if mode == "FAST"
            else source_contents
        )

        print(
            "\nExtracting competitive intelligence from "
            f"{len(competitive_sources)} sources..."
        )

        for source, content in competitive_sources:
            try:
                item = self.competitive_intelligence.extract(
                    source=source,
                    content=content,
                )

                if item is not None:
                    competitive_intelligence.append(item)

            except Exception as exc:
                print(
                    "Competitive intelligence extraction failed "
                    f"for {source.url}: {exc}"
                )

        # Generate the final research report.
        print("\nGenerating executive research report...")

        report = self.report_generator.generate(
            topic=research_objective.topic,
            claims=claims,
            insights=insights,
            contradictions=contradictions,
            competitive_intelligence=competitive_intelligence,
        )

        print("Executive report generated.")

        # ---------------------------------------------------------
        # 10. MARKDOWN AND PDF EXPORT
        # ---------------------------------------------------------
        print("\n[10/10] Exporting research reports...")

        report_path = self.report_exporter.export_markdown(
            report=report,
            output_path="reports/research_report.md",
        )

        print(f"Markdown report saved: {report_path}")

        pdf_report_path = self.pdf_report_exporter.export(
            report=report,
            output_path="reports/research_report.pdf",
        )

        print(f"PDF report saved: {pdf_report_path}")

        # ---------------------------------------------------------
        # FINAL SUMMARY
        # ---------------------------------------------------------
        has_warnings = (
            failed_research_tasks > 0
            or failed_evidence_batches > 0
            or contradiction_status != "completed"
        )

        print("\n" + "=" * 70)

        if has_warnings:
            print("PIPELINE COMPLETED WITH WARNINGS")
        else:
            print("PIPELINE COMPLETED SUCCESSFULLY")

        print("=" * 70)
        print(f"Mode                 : {mode}")
        print(f"Research tasks used  : {len(selected_tasks)}")
        print(f"Failed research tasks: {failed_research_tasks}")
        print(f"Failed evidence batches: {failed_evidence_batches}")
        print(f"Sources collected    : {len(all_sources)}")
        print(f"Webpages extracted   : {len(source_contents)}")
        print(f"Evidence records     : {len(evidence_records)}")
        print(f"Claims generated     : {len(claims)}")
        print(f"Contradictions       : {len(contradictions)}")
        print(f"Insights generated   : {len(insights)}")
        print(f"Competitive records  : {len(competitive_intelligence)}")
        print(f"Evidence ledger JSON : {ledger_json_path}")
        print(f"Evidence ledger MD   : {ledger_markdown_path}")
        print(f"Metrics file         : {metrics_path}")
        print(f"Markdown report      : {report_path}")
        print(f"PDF report           : {pdf_report_path}")
        print("=" * 70)

        # Keep the dictionary return format for dashboard.py.
        
        return {
            "pipeline_status": (
                "completed_with_warnings"
                if has_warnings
                else "completed"
            ),
            "contradiction_detection_status": (
                contradiction_status
            ),
            "report_path": report_path,
            "pdf_report_path": pdf_report_path,
            "ledger_json_path": ledger_json_path,
            "ledger_markdown_path": ledger_markdown_path,
            "metrics_path": metrics_path,
            "metrics": metrics,
        }
