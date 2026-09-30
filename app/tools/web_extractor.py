import requests
from bs4 import BeautifulSoup


class WebContentExtractor:
    """Extracts readable text content from a webpage."""

    def extract(self, url: str) -> str:
        """Fetch a webpage and return its readable text."""

        if not url.strip():
            raise ValueError("URL cannot be empty.")

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/154.0 Safari/537.36"
                )
            },
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for element in soup(
            ["script", "style", "noscript"]
        ):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True,
        )

        if not text:
            raise ValueError(
                f"No readable text found at URL: {url}"
            )

        return text