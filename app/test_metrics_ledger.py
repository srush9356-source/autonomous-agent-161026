from app.models.claim import Claim
from app.models.contradiction import Contradiction
from app.models.evidence import Evidence
from app.models.insight import Insight
from app.models.source import Source

from app.services.evidence_ledger import EvidenceLedger
from app.services.research_metrics import ResearchMetrics


# ---------------------------------------------------------
# MOCK SOURCE
# ---------------------------------------------------------

source = Source(
    source_id="SRC-001",
    title="Example Market Research Source",
    url="https://example.com/market-report",
    source_type="web_search_result",
    publisher="Example Research",
    publication_date=None,
    authority_score=0.85,
    relevance_score=0.90,
    freshness_score=0.80,
)


# ---------------------------------------------------------
# MOCK EVIDENCE
# ---------------------------------------------------------

evidence = Evidence(
    evidence_id="EVD-001",
    claim="Market demand increased during the observed period.",
    source_title=source.title,
    source_url=source.url,
    publication_date=None,
    extracted_text=(
        "The source reports increasing market demand "
        "during the observed period."
    ),
    source_type=source.source_type,
    confidence=0.90,
)


# ---------------------------------------------------------
# MOCK CLAIM
# ---------------------------------------------------------

claim = Claim(
    claim_id="CLM-001",
    statement=(
        "Market demand increased during the observed period."
    ),
    evidence_ids=["EVD-001"],
    confidence=0.88,
    status="supported",
)


# ---------------------------------------------------------
# MOCK CONTRADICTION
# ---------------------------------------------------------

contradiction = Contradiction(
    contradiction_id="CON-001",
    claim_a_id="CLM-001",
    claim_b_id="CLM-002",
    explanation="Example contradiction.",
    severity="low",
    confidence=0.70,
)


# ---------------------------------------------------------
# MOCK INSIGHT
# ---------------------------------------------------------

insight = Insight(
    insight_id="INS-001",
    title="Demand Growth",
    explanation=(
        "The available evidence indicates increasing demand."
    ),
    supporting_claim_ids=["CLM-001"],
    confidence=0.85,
    implication=(
        "Further investigation of demand drivers may be useful."
    ),
)


# ---------------------------------------------------------
# EVIDENCE LEDGER TEST
# ---------------------------------------------------------

ledger_service = EvidenceLedger()

ledger = ledger_service.build(
    evidence_records=[evidence],
    claims=[claim],
    insights=[insight],
)

insight_traceability = (
    ledger_service.add_insight_traceability(
        ledger=ledger,
        insights=[insight],
    )
)

assert len(ledger) == 1
assert ledger[0]["claim_id"] == "CLM-001"
assert len(ledger[0]["evidence"]) == 1

assert (
    ledger[0]["evidence"][0]["evidence_id"]
    == "EVD-001"
)

assert len(insight_traceability) == 1

assert (
    insight_traceability[0]["supporting_claims"][0]
    ["claim_id"]
    == "CLM-001"
)


# ---------------------------------------------------------
# METRICS TEST
# ---------------------------------------------------------

metrics_service = ResearchMetrics()

metrics = metrics_service.calculate(
    sources=[source],
    extracted_sources=[source],
    evidence=[evidence],
    claims=[claim],
    contradictions=[contradiction],
    insights=[insight],
)

assert metrics["sources_analyzed"] == 1
assert metrics["sources_successfully_extracted"] == 1
assert metrics["evidence_records"] == 1
assert metrics["claims_generated"] == 1
assert metrics["high_confidence_claims"] == 1
assert metrics["supported_claims"] == 1
assert metrics["contradictions_detected"] == 1
assert metrics["insights_generated"] == 1
assert metrics["evidence_traceability_rate"] == 1.0


# ---------------------------------------------------------
# SUCCESS
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("METRICS + EVIDENCE LEDGER INTEGRATION TEST")
print("=" * 70)

print("\nEvidence Ledger:")
print(ledger)

print("\nInsight Traceability:")
print(insight_traceability)

print("\nResearch Metrics:")
for key, value in metrics.items():
    print(f"{key}: {value}")

print("\n" + "=" * 70)
print("METRICS + EVIDENCE LEDGER TEST PASSED")
print("=" * 70)