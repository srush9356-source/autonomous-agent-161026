from pydantic import BaseModel, Field


class Claim(BaseModel):
    """Represents a research claim supported by evidence."""

    claim_id: str = Field(
        description="Unique identifier for the claim.",
    )

    statement: str = Field(
        min_length=10,
        description="The factual statement derived from research.",
    )

    evidence_ids: list[str] = Field(
        min_length=1,
        description="IDs of evidence records supporting this claim.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the claim from 0.0 to 1.0.",
    )

    status: str = Field(
        default="supported",
        description="Current validation status of the claim.",
    )