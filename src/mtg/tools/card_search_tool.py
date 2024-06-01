import aiohttp
import requests
from langchain.tools import BaseTool

from pydantic import BaseModel, Field

from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from mtg.objects import Card
from mtg.utils.logging import get_logger

logger = get_logger(__name__)


async def send_post_request(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            response_json = await response.json()
            return response_json


class CardSearchInput(BaseModel):
    query: str = Field(description="should be a search query")
    number_of_cards: int = Field(
        default=1, description="number of cards that should be returned"
    )
    sample_results: Optional[bool] = Field(
        default=False,
        description="For more creative responses sample the results from a pool of found cards",
    )


class CardSearchTool(BaseTool):
    name = "mtg_card_search"
    description = (
        "Search for cards in a magic the gathering card database with all cards up to 14.05.2024."
        "You will receive all card info including card specific rulings, attributes and price"
        "You can also choose number of cards you want to receive. For arbitrary queries that are not specific cards, ask for multiple results."
        "An arbitrary query could be 'black removal spells' number_of_cards = 5 sample_results = True"
        "A card name query could be 'Black Lotus' number_of_cards = 1 sample_results = False"
    )
    args_schema: Type[BaseModel] = CardSearchInput
    url: str = "http://localhost:8000/"
    threshold: float = 0.4
    lasso_threshold: float = 0.1

    def _run(
        self,
        query: str,
        number_of_cards: int,
        sample_results: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""

        logger.info(
            f"Triggering Card Search with query: {query}, number_of_cards: {number_of_cards}, sample_results: {sample_results}"
        )

        response = requests.post(
            url=f"{self.url}cards/",
            json={
                "text": query,
                "k": number_of_cards,
                "threshold": self.threshold,
                "lasso_threshold": self.lasso_threshold,
                "sample_results": sample_results,
            },
        )
        response = response.json()
        cards_text = self._parse_response(response)
        return cards_text

    async def _arun(
        self,
        query: str,
        number_of_cards: int,
        sample_results: bool = False,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""

        logger.info(
            f"Triggering Card Search with query: {query}, number_of_cards: {number_of_cards}, sample_results: {sample_results}"
        )

        payload = {
            "text": query,
            "k": number_of_cards,
            "threshold": self.threshold,
            "lasso_threshold": self.lasso_threshold,
            "sample_results": sample_results,
        }
        response = await send_post_request(f"{self.url}cards/", data=payload)
        cards_text = self._parse_response(response)
        return cards_text

    def _parse_response(self, response: dict) -> list[Card]:
        """parses response to string and saves Cards in history"""

        card_names = set()
        cards = []
        for card in response:
            card_data = card["card"]
            distance = card["distance"]
            card = Card(**card_data)
            logger.debug(f"received card {card.name} distance {distance:.2f}")
            if card.name in card_names:
                continue
            else:
                cards.append(card)
                card_names.add(card.name)

        logger.info(f"received {len(cards)} cards from card search tool")
        cards_text = "\n\n".join([card.to_text() for card in cards])
        if cards:
            return cards_text
        return "No Cards Info found!"
