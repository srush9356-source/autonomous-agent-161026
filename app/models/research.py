from pydantic import BaseModel, Field


class ResearchObjective(BaseModel):
    """Represents the user's main research objective."""

    topic: str = Field(
        min_length=3,
        description="The main topic or subject being researched.",
    )

    objective: str = Field(
        min_length=10,
        description="What the research should determine or analyze.",
    )

    industry: str | None = Field(
        default=None,
        description="Industry or domain relevant to the research.",
    )


class ResearchTask(BaseModel):
    """Represents an individual research task."""

    task_id: str = Field(
        description="Unique identifier for the research task.",
    )

    question: str = Field(
        min_length=5,
        description="Specific research question to investigate.",
    )

    purpose: str = Field(
        min_length=5,
        description="Why this research question is important.",
    )

    priority: int = Field(
        ge=1,
        le=5,
        description="Task priority from 1 to 5.",
    )