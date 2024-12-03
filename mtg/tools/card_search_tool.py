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


async def send_get_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_json = await response.json()
    return response_json


class CardSearchInput(BaseModel):
    query: str = Field(
        description="should be a search query for the name of the card, the oracle text or the card type."
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
    name: str = "list_mtg_cards"
    description: str = (
        "Search for multiple cards in a magic the gathering card database."
        "The Query parameter will search for the oracle text, type and subtype."
        "So you have to rephrase the question of the User to words that will appear on the oracle text of the card."
        "You will receive all card info including card specific rulings, attributes, price and URL. "
        "A query for 'black removal spells' could be: query = 'destroy creature', color_identity = ['B'] "
        "A query for 'white removal spells' could be: query = 'exile creature', color_identity = ['W'] "
        "A query for 'white and blue blink spells' could be: query = 'exile and return to the battlefield', color_identity = ['W', 'U'] "
    )
    args_schema: Type[BaseModel] = CardSearchInput
    url: str = "http://localhost:8000/"
    threshold: float = 0.5
    number_of_cards: int = 20

    def _run(
        self,
        query: str,
        keywords: list[str] = [],
        color_identity: list[str] = [],
        legality: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool to search cards."""

        logger.info(
            (
                f"Triggering Card Search with query: '{query}' "
                f"keywords: [{', '.join(keywords)}], color_identity: [{', '.join(color_identity)}] "
                f"legality: {legality}"
            )
        )

        response = requests.post(
            url=f"{self.url}cards",
            json={
                "text": query,
                "k": self.number_of_cards,
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
        keywords: list[str] = [],
        color_identity: list[str] = [],
        number_of_cards: Optional[int] = None,
        legality: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""

        logger.info(
            (
                f"Triggering Card Search with query: '{query}' "
                f"keywords: [{', '.join(keywords)}], color_identity: [{', '.join(color_identity)}] "
                f"legality: {legality}"
            )
        )

        payload = {
            "text": query,
            "k": self.number_of_cards,
            "keywords": keywords,
            "color_identity": color_identity,
            "legality": legality,
            "threshold": self.threshold,
        }
        response = await send_post_request(f"{self.url}cards", data=payload)
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

        logger.info(
            f"received cards [{','.join([card.name for card in cards])}] from card search tool"
        )
        cards_text = "\n\n".join([card.to_text() for card in cards])
        if cards:
            return cards_text
        return "No Cards Info found!"


class CardNameSearchInput(BaseModel):
    card_name: str = Field(description="The name of the card.")


class CardNameSearchTool(CardSearchTool):
    name: str = "search_mtg_card_name"
    description: str = (
        "Search for a specific magic the gathering card in the card database. "
        "Example: card_name = 'Black Lotus'"
    )
    args_schema: Type[BaseModel] = CardNameSearchInput

    def _run(
        self,
        card_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool to search for a specific card."""

        logger.info(f"Triggering Card Name Search with : '{card_name}' ")

        response = requests.get(url=f"{self.url}card_name/{card_name}")
        response = response.json()
        cards_text = self._parse_response([response])
        return cards_text

    async def _arun(
        self,
        card_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool to search for a specific card asynchronous."""
        logger.info(f"Triggering Card Name Search with : '{card_name}' ")

        response = await send_get_request(url=f"{self.url}card_name/{card_name}")
        cards_text = self._parse_response([response])
        return cards_text
