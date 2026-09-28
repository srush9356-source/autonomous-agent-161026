from pydantic import BaseModel, Field


class RelevanceEvaluation(BaseModel):
    """Structured evaluation of a source's relevance."""

    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Relevance score from 0.0 to 1.0.",
    )

    reason: str = Field(
        min_length=5,
        description="Brief explanation for the relevance score.",
    )