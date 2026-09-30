from pydantic import BaseModel, Field


class Contradiction(BaseModel):
    """Represents a detected conflict between research claims."""

    contradiction_id: str = Field(
        description="Unique identifier for the contradiction."
    )
    claim_a_id: str = Field(
        description="ID of the first conflicting claim."
    )
    claim_b_id: str = Field(
        description="ID of the second conflicting claim."
    )
    explanation: str = Field(
        min_length=10,
        description="Explanation of why the claims conflict."
    )
    severity: str = Field(
        description="Severity of the contradiction."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that the contradiction is genuine."
    )