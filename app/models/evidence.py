from datetime import date

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Represents a piece of evidence collected during research."""

    evidence_id: str = Field(
        description="Unique identifier for the evidence.",
    )

    claim: str = Field(
        min_length=5,
        description="Claim supported by the evidence.",
    )

    source_title: str = Field(
        min_length=3,
        description="Title of the source.",
    )

    source_url: str = Field(
        min_length=5,
        description="URL of the source.",
    )

    publication_date: date | None = Field(
        default=None,
        description="Publication date of the source, if available.",
    )

    extracted_text: str = Field(
        min_length=10,
        description="Relevant text extracted from the source.",
    )

    source_type: str = Field(
        description="Type of source, such as report, news, company website, or research paper.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the evidence from 0.0 to 1.0.",
    )