from app.agents.planner import ResearchPlanner
from app.models.research import ResearchObjective


def main():
    objective = ResearchObjective(
        topic="Indian fruit pulp market",
        objective=(
            "Analyze market trends, major competitors, "
            "pricing signals, and export opportunities "
            "for Gadage Agro."
        ),
        industry="Food Processing",
    )

    print("=" * 60)
    print("AUTONOMOUS MARKET & RESEARCH INTELLIGENCE AGENT")
    print("=" * 60)

    print("\nResearch Objective")
    print("-" * 60)
    print(f"Topic: {objective.topic}")
    print(f"Industry: {objective.industry}")
    print(f"Objective: {objective.objective}")

    print("\nGenerating research plan...\n")

    planner = ResearchPlanner()
    tasks = planner.create_plan(objective)

    print("Generated Research Tasks")
    print("-" * 60)

    for task in tasks:
        print(f"\n{task.task_id}")
        print(f"Question : {task.question}")
        print(f"Purpose  : {task.purpose}")
        print(f"Priority : {task.priority}")

    print("\n" + "=" * 60)
    print(f"Successfully generated {len(tasks)} validated research tasks.")
    print("=" * 60)


if __name__ == "__main__":
    main()