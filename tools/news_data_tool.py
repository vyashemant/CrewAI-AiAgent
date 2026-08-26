from typing import Type
import os

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ============================================================
# INPUT SCHEMA
# ============================================================

class NewsDataInput(BaseModel):
    """Input schema for the News Data Tool."""

    ticker: str = Field(
        ...,
        description=(
            "Stock ticker symbol of the publicly traded company. "
            "Examples: AAPL, MSFT, NVDA."
        )
    )

    limit: int = Field(
        default=3,
        ge=1,
        le=3,
        description=(
            "Maximum number of news articles to retrieve. "
            "The free Marketaux plan supports up to 3 articles "
            "per news request."
        )
    )


# ============================================================
# NEWS DATA TOOL
# ============================================================

class NewsDataTool(BaseTool):
    """
    Retrieve recent financial news for a publicly traded company
    using the Marketaux API.
    """

    name: str = "News Data Tool"

    description: str = (
        "Retrieves recent financial and stock-market news for a "
        "company using its ticker symbol. Returns article titles, "
        "descriptions, publication timestamps, source information, "
        "URLs, and entity information."
    )

    args_schema: Type[BaseModel] = NewsDataInput

    BASE_URL: str = "https://api.marketaux.com/v1/news/all"

    # ========================================================
    # RUN
    # ========================================================

    def _run(
        self,
        ticker: str,
        limit: int = 3
    ) -> str:

        api_token = os.getenv("MARKETAUX_API_KEY")

        if not api_token:
            raise ValueError(
                "MARKETAUX_API_KEY not found. "
                "Add it to your .env file."
            )

        ticker = ticker.strip().upper()

        if not ticker:
            raise ValueError(
                "Ticker symbol cannot be empty."
            )

        if limit < 1 or limit > 3:
            raise ValueError(
                "limit must be between 1 and 3."
            )

        params = {
            "api_token": api_token,
            "symbols": ticker,
            "filter_entities": "true",
            "language": "en",
            "limit": limit,
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=15
            )

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Marketaux API request failed: {exc}"
            ) from exc

        if response.status_code != 200:
            raise RuntimeError(
                "Marketaux API returned an error. "
                f"Status code: {response.status_code}. "
                f"Response: {response.text[:500]}"
            )

        try:
            data = response.json()

        except ValueError as exc:
            raise RuntimeError(
                "Marketaux API returned invalid JSON."
            ) from exc

        # ----------------------------------------------------
        # API-level error
        # ----------------------------------------------------

        if "error" in data:
            error = data.get("error", {})

            if isinstance(error, dict):
                message = error.get(
                    "message",
                    "Unknown Marketaux API error."
                )
            else:
                message = str(error)

            raise RuntimeError(
                f"Marketaux API error: {message}"
            )

        articles = data.get("data", [])

        if not articles:
            return str({
                "source": "Marketaux",
                "ticker": ticker,
                "articles": [],
                "article_count": 0,
                "message": (
                    "No recent financial news was found "
                    "for this ticker."
                )
            })

        cleaned_articles = []

        for article in articles:

            entities = []

            for entity in article.get("entities", []):

                entities.append({
                    "symbol": entity.get("symbol"),
                    "name": entity.get("name"),
                    "type": entity.get("type"),
                    "industry": entity.get("industry"),
                    "country": entity.get("country"),
                    "match_score": entity.get("match_score"),
                    "sentiment_score": entity.get(
                        "sentiment_score"
                    )
                })

            cleaned_articles.append({
                "uuid": article.get("uuid"),

                "title": article.get("title"),

                "description": article.get(
                    "description"
                ),

                "snippet": article.get(
                    "snippet"
                ),

                "url": article.get("url"),

                "published_at": article.get(
                    "published_at"
                ),

                "source": article.get(
                    "source"
                ),

                "source_domain": article.get(
                    "source_domain"
                ),

                "language": article.get(
                    "language"
                ),

                "entities": entities
            })

        result = {
            "source": "Marketaux",
            "ticker": ticker,
            "article_count": len(cleaned_articles),
            "articles": cleaned_articles
        }

        return str(result)