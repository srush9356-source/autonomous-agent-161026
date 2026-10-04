from pydantic import BaseModel, Field


class ResearchReport(BaseModel):
    """Structured executive research report."""

    title: str = Field(min_length=5)
    executive_summary: str = Field(min_length=20)
    key_findings: list[str] = Field(min_length=1)
    insights: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    competitive_summary: list[str] = Field(default_factory=list)
    conclusion: str = Field(min_length=20)