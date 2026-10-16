from app.models.research import ResearchObjective
from app.pipeline import ResearchPipeline


research_objective = ResearchObjective(
    topic="Indian fruit pulp market",
    industry="Food Processing",
    objective=(
        "Analyze current market trends, major competitors, pricing signals, "
        "growth opportunities, and risks in the Indian fruit pulp market."
    ),
)

pipeline = ResearchPipeline()

report_path = pipeline.run(research_objective)

print("\nFinal report:")
print(report_path)