import json

from app.llm.client import LLMClient
from app.models.claim import Claim
from app.models.evidence import Evidence


class ClaimExtractor:
    """
    Converts evidence records into concise research claims.

    Evidence is processed in larger batches to reduce LLM API usage.
    """

    def __init__(self):
        self.llm = LLMClient()

    def extract(
        self,
        evidence_records: list[Evidence],
        batch_size: int = 25,
    ) -> list[Claim]:
        """
        Convert evidence into research claims.

        Args:
            evidence_records:
                Evidence collected from research sources.

            batch_size:
                Number of evidence records processed per LLM call.

        Returns:
            List of Claim objects.
        """

        if not evidence_records:
            return []

        all_claims = []

        for batch_start in range(
            0,
            len(evidence_records),
            batch_size,
        ):

            batch = evidence_records[
                batch_start:
                batch_start + batch_size
            ]

            print(
                f"Processing claim batch "
                f"{batch_start // batch_size + 1} "
                f"({len(batch)} evidence records)..."
            )

            evidence_blocks = []

            for evidence in batch:

                # Keep the prompt bounded.
                supporting_text = (
                    evidence.extracted_text or ""
                )[:1800]

                evidence_blocks.append(
                    f"""
EVIDENCE ID:
{evidence.evidence_id}

SOURCE:
{evidence.source_title}

CLAIM FROM SOURCE:
{evidence.claim}

SUPPORTING TEXT:
{supporting_text}

EVIDENCE CONFIDENCE:
{evidence.confidence}
"""
                )

            evidence_text = "\n".join(
                evidence_blocks
            )

            prompt = f"""
You are a senior research analyst working in an
enterprise market research intelligence system.

Convert the evidence below into concise,
non-duplicated, factual research claims.

EVIDENCE:
{evidence_text}

RULES:

- Use ONLY the provided evidence.
- Do not invent facts.
- Do not use outside knowledge.
- Combine closely related evidence when appropriate.
- Every claim MUST reference one or more exact evidence IDs.
- Preserve evidence IDs exactly.
- Do not create evidence IDs.
- Avoid duplicate or nearly identical claims.
- Keep claims specific and factual.
- Do not make recommendations.
- Do not make unsupported assumptions.
- Confidence must be between 0.0 and 1.0.
- Status should normally be "supported".
- If evidence is weak or incomplete, reduce confidence.
- Prefer fewer high-quality claims over many repetitive claims.

Return ONLY valid JSON.

Required format:

[
    {{
        "statement": "Concise factual research claim",
        "evidence_ids": ["EVD-001"],
        "confidence": 0.0,
        "status": "supported"
    }}
]

Do not include markdown.
Do not include explanations outside the JSON.
"""

            try:

                response = self.llm.generate(
                    prompt
                )

                claim_data = json.loads(
                    response
                )

            except json.JSONDecodeError:

                print(
                    f"Warning: claim batch "
                    f"{batch_start // batch_size + 1} "
                    f"returned invalid JSON. "
                    f"Skipping batch."
                )

                continue

            except Exception as exc:

                print(
                    f"Warning: claim batch "
                    f"{batch_start // batch_size + 1} "
                    f"failed: {exc}"
                )

                continue

            # Validate and convert returned claims.
            for item in claim_data:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                statement = item.get(
                    "statement"
                )

                evidence_ids = item.get(
                    "evidence_ids",
                    [],
                )

                confidence = item.get(
                    "confidence",
                    0.0,
                )

                status = item.get(
                    "status",
                    "supported",
                )

                if not statement:
                    continue

                if not evidence_ids:
                    continue

                # Only retain evidence IDs that actually
                # exist in the current evidence collection.
                valid_evidence_ids = [
                    evidence_id
                    for evidence_id in evidence_ids
                    if any(
                        evidence.evidence_id
                        == evidence_id
                        for evidence in evidence_records
                    )
                ]

                if not valid_evidence_ids:
                    continue

                all_claims.append(
                    Claim(
                        claim_id=(
                            f"CLM-"
                            f"{len(all_claims) + 1:03d}"
                        ),
                        statement=statement,
                        evidence_ids=valid_evidence_ids,
                        confidence=float(
                            confidence
                        ),
                        status=status,
                    )
                )

        print(
            f"Total claims generated: "
            f"{len(all_claims)}"
        )

        return all_claims