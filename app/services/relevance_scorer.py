from app.llm.client import LLMClient
from app.models.relevance import RelevanceEvaluation
from app.models.research import ResearchObjective
from app.models.source import Source


class RelevanceScorer:
    """Calculates source relevance using the configured LLM."""

    def __init__(self):
        self.llm = LLMClient()

    def score(
        self,
        source: Source,
        research_objective: ResearchObjective,
    ) -> Source:
        """Calculate the relevance of a source."""

        prompt = f"""
You are a research-source relevance evaluator.

Evaluate how relevant the following source is to the research objective.

RESEARCH OBJECTIVE
Topic: {research_objective.topic}
Industry: {research_objective.industry}
Objective: {research_objective.objective}

SOURCE
Title: {source.title}
Publisher: {source.publisher}
URL: {source.url}

Evaluate relevance based primarily on whether the source
addresses the research topic and objective.

Scoring:

0.0 = Completely unrelated
0.25 = Slightly related
0.50 = Partially relevant
0.75 = Highly relevant
1.0 = Directly relevant
"""

        evaluation = self.llm.generate_structured(
            prompt=prompt,
            response_model=RelevanceEvaluation,
        )

        return source.model_copy(
            update={
                "relevance_score": evaluation.relevance_score,
            }
        )