import json
from pathlib import Path


class MetricsExporter:
    """Exports research metrics as JSON."""

    def export(
        self,
        metrics: dict,
        output_path: str = (
            "reports/research_metrics.json"
        ),
    ) -> str:

        path = Path(output_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                metrics,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return str(path)