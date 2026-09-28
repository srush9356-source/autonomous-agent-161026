import os
from dataclasses import dataclass

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


@dataclass
class SearchResult:
    """Represents a result returned by a web search."""

    title: str
    url: str
    snippet: str


class WebSearchTool:
    """Performs web searches using Tavily."""

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY is not configured. "
                "Please add it to the .env file."
            )

        self.client = TavilyClient(api_key=api_key)

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        """Search the web and return structured results."""

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
        )

        results = []

        for item in response.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                )
            )

        return results