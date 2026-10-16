from statistics import mean

from app.models.claim import Claim
from app.models.contradiction import Contradiction
from app.models.evidence import Evidence
from app.models.insight import Insight
from app.models.source import Source


class ResearchMetrics:
    """Calculates quality, coverage, confidence, and traceability metrics."""

    def calculate(
        self,
        sources: list[Source],
        extracted_sources: list[Source],
        evidence: list[Evidence],
        claims: list[Claim],
        contradictions: list[Contradiction],
        insights: list[Insight],
    ) -> dict:

        source_count = len(sources)
        extracted_count = len(extracted_sources)
        evidence_count = len(evidence)
        claim_count = len(claims)
        contradiction_count = len(contradictions)
        insight_count = len(insights)

        # ---------------------------------------------------------
        # SOURCE COVERAGE
        # ---------------------------------------------------------

        extraction_success_rate = (
            extracted_count / source_count
            if source_count
            else 0.0
        )

        source_quality_scores = [
            (
                source.authority_score
                + source.relevance_score
                + source.freshness_score
            ) / 3
            for source in sources
        ]

        average_source_authority = (
            mean(
                source.authority_score
                for source in sources
            )
            if sources
            else 0.0
        )

        average_source_relevance = (
            mean(
                source.relevance_score
                for source in sources
            )
            if sources
            else 0.0
        )

        average_source_freshness = (
            mean(
                source.freshness_score
                for source in sources
            )
            if sources
            else 0.0
        )

        average_source_quality = (
            mean(source_quality_scores)
            if source_quality_scores
            else 0.0
        )

        high_quality_sources = [
            source
            for source in sources
            if (
                (
                    source.authority_score
                    + source.relevance_score
                    + source.freshness_score
                ) / 3
            ) >= 0.75
        ]

        # ---------------------------------------------------------
        # EVIDENCE QUALITY
        # ---------------------------------------------------------

        high_confidence_evidence = [
            item
            for item in evidence
            if item.confidence >= 0.75
        ]

        average_evidence_confidence = (
            mean(
                item.confidence
                for item in evidence
            )
            if evidence
            else 0.0
        )

        evidence_per_source = (
            evidence_count / extracted_count
            if extracted_count
            else 0.0
        )

        # ---------------------------------------------------------
        # CLAIM QUALITY
        # ---------------------------------------------------------

        high_confidence_claims = [
            claim
            for claim in claims
            if claim.confidence >= 0.75
        ]

        average_claim_confidence = (
            mean(
                claim.confidence
                for claim in claims
            )
            if claims
            else 0.0
        )

        supported_claims = [
            claim
            for claim in claims
            if claim.status == "supported"
        ]

        claim_support_rate = (
            len(supported_claims) / claim_count
            if claim_count
            else 0.0
        )

        # ---------------------------------------------------------
        # TRACEABILITY
        # ---------------------------------------------------------

        evidence_linked_claims = [
            claim
            for claim in claims
            if claim.evidence_ids
        ]

        evidence_traceability_rate = (
            len(evidence_linked_claims)
            / claim_count
            if claim_count
            else 0.0
        )

        # ---------------------------------------------------------
        # INSIGHT QUALITY
        # ---------------------------------------------------------

        average_insight_confidence = (
            mean(
                insight.confidence
                for insight in insights
            )
            if insights
            else 0.0
        )

        # ---------------------------------------------------------
        # SOURCE DIVERSITY
        # ---------------------------------------------------------

        source_types = {
            source.source_type
            for source in sources
            if source.source_type
        }

        source_diversity = len(source_types)

        # ---------------------------------------------------------
        # OVERALL RESEARCH QUALITY
        # ---------------------------------------------------------

        overall_quality = mean(
            [
                average_source_quality,
                average_evidence_confidence,
                average_claim_confidence,
                evidence_traceability_rate,
            ]
        )

        # ---------------------------------------------------------
        # RETURN METRICS
        # ---------------------------------------------------------

        return {
            "sources_analyzed": source_count,
            "sources_successfully_extracted": extracted_count,
            "extraction_success_rate": round(
                extraction_success_rate,
                3,
            ),

            "high_quality_sources": len(
                high_quality_sources
            ),

            "average_source_authority": round(
                average_source_authority,
                3,
            ),

            "average_source_relevance": round(
                average_source_relevance,
                3,
            ),

            "average_source_freshness": round(
                average_source_freshness,
                3,
            ),

            "average_source_quality": round(
                average_source_quality,
                3,
            ),

            "source_diversity": source_diversity,

            "evidence_records": evidence_count,

            "high_confidence_evidence": len(
                high_confidence_evidence
            ),

            "average_evidence_confidence": round(
                average_evidence_confidence,
                3,
            ),

            "evidence_per_source": round(
                evidence_per_source,
                3,
            ),

            "claims_generated": claim_count,

            "high_confidence_claims": len(
                high_confidence_claims
            ),

            "supported_claims": len(
                supported_claims
            ),

            "claim_support_rate": round(
                claim_support_rate,
                3,
            ),

            "evidence_traceability_rate": round(
                evidence_traceability_rate,
                3,
            ),

            "contradictions_detected": (
                contradiction_count
            ),

            "insights_generated": insight_count,

            "average_claim_confidence": round(
                average_claim_confidence,
                3,
            ),

            "average_insight_confidence": round(
                average_insight_confidence,
                3,
            ),

            "overall_research_quality": round(
                overall_quality,
                3,
            ),
        }