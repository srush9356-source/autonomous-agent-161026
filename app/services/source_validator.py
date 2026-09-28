from datetime import date

from app.models.source import Source
from app.tools.search import SearchResult


class SourceValidator:
    """Converts raw search results into validated source records."""

    def validate(
        self,
        search_results: list[SearchResult],
    ) -> list[Source]:
        """Validate and structure search results as Source objects."""

        validated_sources = []

        for index, result in enumerate(search_results, start=1):
            if not result.title.strip():
                continue

            if not result.url.strip():
                continue

            source = Source(
                source_id=f"SRC-{index:03d}",
                title=result.title,
                url=result.url,
                source_type="web_search_result",
                publisher=self._extract_publisher(result.url),
                publication_date=None,
                authority_score=0.5,
                relevance_score=0.5,
                freshness_score=0.5,
            )

            validated_sources.append(source)

        return validated_sources

    @staticmethod
    def _extract_publisher(url: str) -> str:
        """Extract a simple publisher name from a URL."""

        cleaned_url = (
            url.replace("https://", "")
            .replace("http://", "")
        )

        domain = cleaned_url.split("/")[0]

        return domain.replace("www.", "")