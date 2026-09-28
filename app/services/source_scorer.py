from urllib.parse import urlparse

from app.models.source import Source


class SourceScorer:
    """Calculates source quality scores using source metadata."""

    def score(self, source: Source) -> Source:
        """Calculate and return updated source scores."""

        authority_score = self._calculate_authority(source)

        return source.model_copy(
            update={
                "authority_score": authority_score,
            }
        )

    def _calculate_authority(self, source: Source) -> float:
        """
        Estimate source authority using general source signals.

        The calculation is intentionally domain-independent.
        """

        score = 0.5

        domain = self._extract_domain(source.url)

        # Signal 1: identifiable publisher
        if source.publisher and source.publisher != domain:
            score += 0.05

        # Signal 2: recognizable source type
        source_type = source.source_type.lower()

        if any(
            keyword in source_type
            for keyword in (
                "government",
                "research",
                "academic",
                "journal",
                "official",
            )
        ):
            score += 0.15

        # Signal 3: secure HTTPS source
        if source.url.lower().startswith("https://"):
            score += 0.05

        return min(score, 1.0)

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract the domain from a source URL."""

        parsed_url = urlparse(url)

        return parsed_url.netloc.lower().replace(
            "www.",
            "",
        )