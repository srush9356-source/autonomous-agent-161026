import json

from app.llm.client import LLMClient
from app.models.research import ResearchObjective, ResearchTask


class ResearchPlanner:
    """Converts a research objective into structured research tasks."""

    def __init__(self):
        self.llm = LLMClient()

    def create_plan(
        self,
        research_objective: ResearchObjective,
    ) -> list[ResearchTask]:
        """Generate structured research tasks from the objective."""

        prompt = f"""
You are a senior market research planning analyst.

Create a focused research plan for the following objective.

Topic:
{research_objective.topic}

Industry:
{research_objective.industry}

Objective:
{research_objective.objective}

Generate exactly 5 research tasks.

The tasks should cover different aspects of the objective,
such as competitors, products, pricing, trends, opportunities,
risks, customers, or other relevant areas.

Return ONLY valid JSON in this format:

[
    {{
        "task_id": "TASK-001",
        "question": "Specific research question",
        "purpose": "Why this question matters",
        "priority": 5
    }}
]

Priority must be an integer from 1 to 5.
Do not include markdown.
Do not include explanations outside the JSON.
"""

        response = self.llm.generate(prompt)

        try:
            task_data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The research planner returned invalid JSON."
            ) from exc

        return [
            ResearchTask(**task)
            for task in task_data
        ]