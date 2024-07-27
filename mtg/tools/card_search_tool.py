import aiohttp
import requests
from langchain.tools import BaseTool

from pydantic import BaseModel, Field

from typing import Optional, Type, Literal
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
    query: str = Field(
        description="should be a search query for the name of the card, the oracle text or the card type."
    )
    number_of_cards: int = Field(
        default=1, description="Number of cards that should be returned"
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Filter for certain Magic the Gathering Keywords. e.g. 'First Strike', 'Deathtouch'... ",
    )
    color_identity: list[Literal["W", "U", "B", "R", "G"]] = Field(
        default_factory=list,
        description="Filter for the color identity of the cards. e.g. 'W', 'U', 'B', 'R', 'G'",
    )
    legality: str = Field(
        default=None,
        description="Filter for if the card is legal is a certain playmode e.g. 'commander', 'modern'...",
    )


class CardSearchTool(BaseTool):
    name = "mtg_card_search"
    description = (
        "Search for cards in a magic the gathering card database with all cards up to 22.07.2024. "
        "The Query parameter will search for the oracle text or name of the card. So you have to rephrase the question of the User "
        "to words that will appear on the oracle text of the card."
        "You will receive all card info including card specific rulings, attributes, price and URL. "
        "You can also choose number of cards you want to receive. For arbitrary queries that are not specific cards, ask for multiple results. "
        "A query for 'black removal spells' could be: query = 'destroy creature', number_of_cards = 10, color_identity = ['B'] "
        "A query for 'white removal spells' could be: query = 'exile creature', number_of_cards = 10, color_identity = ['W'] "
        "A query for 'white and blue blink spells' could be: query = 'exile and return to the battlefield', number_of_cards = 10, color_identity = ['W', 'U'] "
        "A card name query for the card 'Black Lotus' could be: query = 'Black Lotus' number_of_cards = 1"
    )
    args_schema: Type[BaseModel] = CardSearchInput
    url: str = "http://localhost:8000/"
    threshold: float = 0.5

    def _run(
        self,
        query: str,
        number_of_cards: int = 1,
        keywords: list[str] = [],
        color_identity: list[str] = [],
        legality: str = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool to search cards."""

        logger.info(
            (
                f"Triggering Card Search with query: {query}, number_of_cards: {number_of_cards}, "
                f"keywords: {','.join(keywords)}, color_identity: {','.join(color_identity)} "
                f"legality: {legality}"
            )
        )

        response = requests.post(
            url=f"{self.url}cards/",
            json={
                "text": query,
                "k": number_of_cards,
                "keywords": keywords,
                "color_identity": color_identity,
                "legality": legality,
                "threshold": self.threshold,
            },
        )
        response = response.json()
        cards_text = self._parse_response(response)
        return cards_text

    async def _arun(
        self,
        query: str,
        number_of_cards: int = 1,
        keywords: list[str] = [],
        color_identity: list[str] = [],
        legality: str = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""

        logger.info(
            (
                f"Triggering Card Search with query: {query}, number_of_cards: {number_of_cards}, "
                f"keywords: {','.join(keywords)}, color_identity: {','.join(color_identity)} "
                f"legality: {legality}"
            )
        )

        payload = {
            "text": query,
            "k": number_of_cards,
            "keywords": keywords,
            "color_identity": color_identity,
            "legality": legality,
            "threshold": self.threshold,
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
