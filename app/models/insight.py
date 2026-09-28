from pydantic import BaseModel, Field


class Insight(BaseModel):
    """Represents an analytical insight derived from validated claims."""

    insight_id: str = Field(
        description="Unique identifier for the insight.",
    )

    title: str = Field(
        min_length=5,
        description="Short title describing the insight.",
    )

    explanation: str = Field(
        min_length=20,
        description="Explanation of the insight and its significance.",
    )

    supporting_claim_ids: list[str] = Field(
        min_length=1,
        description="IDs of claims supporting this insight.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the insight from 0.0 to 1.0.",
    )

    implication: str = Field(
        min_length=10,
        description="Potential business or strategic implication.",
    )