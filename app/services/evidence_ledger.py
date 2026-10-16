import json
from pathlib import Path

from app.models.claim import Claim
from app.models.evidence import Evidence
from app.models.insight import Insight


class EvidenceLedger:
    """
    Builds an evidence-to-claim traceability ledger.

    The ledger connects:
        Claims → Evidence → Sources

    It also connects:
        Insights → Claims → Evidence
    """

    def build(
        self,
        evidence_records: list[Evidence],
        claims: list[Claim],
        insights: list[Insight],
    ) -> list[dict]:

        evidence_map = {
            evidence.evidence_id: evidence
            for evidence in evidence_records
        }

        claim_map = {
            claim.claim_id: claim
            for claim in claims
        }

        ledger = []

        for claim in claims:

            claim_evidence = []

            for evidence_id in claim.evidence_ids:

                evidence = evidence_map.get(
                    evidence_id
                )

                if evidence is None:
                    continue

                claim_evidence.append(
                    {
                        "evidence_id": evidence.evidence_id,
                        "source_title": evidence.source_title,
                        "source_url": evidence.source_url,
                        "publication_date": (
                            evidence.publication_date
                        ),
                        "source_type": evidence.source_type,
                        "claim_from_source": evidence.claim,
                        "supporting_text": (
                            evidence.extracted_text
                        ),
                        "evidence_confidence": (
                            evidence.confidence
                        ),
                    }
                )

            ledger.append(
                {
                    "claim_id": claim.claim_id,
                    "claim": claim.statement,
                    "claim_confidence": claim.confidence,
                    "status": claim.status,
                    "evidence": claim_evidence,
                }
            )

        return ledger

    def add_insight_traceability(
        self,
        ledger: list[dict],
        insights: list[Insight],
    ) -> list[dict]:

        claim_to_evidence = {
            item["claim_id"]: item["evidence"]
            for item in ledger
        }

        insight_records = []

        for insight in insights:

            supporting_claims = []

            for claim_id in (
                insight.supporting_claim_ids
            ):

                supporting_claims.append(
                    {
                        "claim_id": claim_id,
                        "evidence": claim_to_evidence.get(
                            claim_id,
                            [],
                        ),
                    }
                )

            insight_records.append(
                {
                    "insight_id": insight.insight_id,
                    "title": insight.title,
                    "confidence": insight.confidence,
                    "supporting_claims": (
                        supporting_claims
                    ),
                }
            )

        return insight_records

    def export_json(
        self,
        ledger: list[dict],
        insights: list[dict],
        output_path: str = (
            "reports/evidence_ledger.json"
        ),
    ) -> str:

        path = Path(output_path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "claims": ledger,
            "insights": insights,
        }

        path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return str(path)

    def export_markdown(
        self,
        ledger: list[dict],
        insights: list[dict],
        output_path: str = (
            "reports/evidence_ledger.md"
        ),
    ) -> str:

        path = Path(output_path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        lines = [
            "# Evidence Ledger",
            "",
            (
                "This ledger provides traceability from "
                "research claims to their supporting evidence "
                "and source URLs."
            ),
            "",
        ]

        for item in ledger:

            lines.extend(
                [
                    f"## {item['claim_id']}",
                    "",
                    f"**Claim:** {item['claim']}",
                    "",
                    (
                        f"**Claim confidence:** "
                        f"{item['claim_confidence']:.2f}"
                    ),
                    "",
                    f"**Status:** {item['status']}",
                    "",
                    "### Supporting Evidence",
                    "",
                ]
            )

            if not item["evidence"]:
                lines.extend(
                    [
                        "No supporting evidence found.",
                        "",
                    ]
                )
                continue

            for evidence in item["evidence"]:

                lines.extend(
                    [
                        f"#### {evidence['evidence_id']}",
                        "",
                        (
                            f"**Source:** "
                            f"{evidence['source_title']}"
                        ),
                        "",
                        (
                            f"**URL:** "
                            f"{evidence['source_url']}"
                        ),
                        "",
                        (
                            f"**Source type:** "
                            f"{evidence['source_type']}"
                        ),
                        "",
                        (
                            f"**Evidence confidence:** "
                            f"{evidence['evidence_confidence']:.2f}"
                        ),
                        "",
                        "**Source claim:**",
                        "",
                        evidence["claim_from_source"],
                        "",
                        "**Supporting text:**",
                        "",
                        evidence["supporting_text"],
                        "",
                        "---",
                        "",
                    ]
                )

        lines.extend(
            [
                "# Insight Traceability",
                "",
            ]
        )

        for insight in insights:

            lines.extend(
                [
                    f"## {insight['insight_id']}",
                    "",
                    f"**{insight['title']}**",
                    "",
                    (
                        f"**Confidence:** "
                        f"{insight['confidence']:.2f}"
                    ),
                    "",
                ]
            )

            for claim in (
                insight["supporting_claims"]
            ):

                lines.extend(
                    [
                        (
                            f"### Supporting Claim: "
                            f"{claim['claim_id']}"
                        ),
                        "",
                    ]
                )

                for evidence in claim["evidence"]:

                    lines.extend(
                        [
                            (
                                f"- "
                                f"{evidence['evidence_id']} — "
                                f"{evidence['source_title']}"
                            ),
                            (
                                f"  - URL: "
                                f"{evidence['source_url']}"
                            ),
                        ]
                    )

                lines.append("")

        path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return str(path)