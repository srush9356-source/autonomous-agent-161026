from datetime import date

from pydantic import BaseModel, Field


class Source(BaseModel):
    """Represents metadata about a research source."""

    source_id: str = Field(
        description="Unique identifier for the source.",
    )

    title: str = Field(
        min_length=3,
        description="Title of the source.",
    )

    url: str = Field(
        min_length=5,
        description="URL of the source.",
    )

    source_type: str = Field(
        description=(
            "Type of source, such as government report, "
            "research paper, news article, or company website."
        ),
    )

    publisher: str = Field(
        min_length=2,
        description="Organization or publisher responsible for the source.",
    )

    publication_date: date | None = Field(
        default=None,
        description="Publication date if available.",
    )

    authority_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Estimated authority of the source.",
    )

    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Relevance of the source to the research objective.",
    )

    freshness_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Freshness of the information.",
    )