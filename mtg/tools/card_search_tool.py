# %%

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
    include_price: bool = Field(
        default=False,
        description="If the current price of the card should be included in the output",
    )


class CardSearchTool(BaseTool):
    name = "mtg_card_search"
    description = "Search for cards in a magic the gathering card database with all cards up to 14.05.2024. You will receive all card info including card specific rulings, attributes and price"
    args_schema: Type[BaseModel] = CardSearchInput
    url: str = "http://localhost:8000/"
    k: int = 10
    threshold: float = 0.4
    lasso_threshold: float = 0.1
    sample_results: bool = False

    def _run(
        self,
        query: str,
        include_price: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""

        response = requests.post(
            url=f"{self.url}cards/",
            json={
                "text": query,
                "k": self.k,
                "threshold": self.threshold,
                "lasso_threshold": self.lasso_threshold,
                "sample_results": self.sample_results,
            },
        )
        response = response.json()
        cards = self._parse_response(response)

        return "\n\n".join(
            [card.to_text(include_price=include_price) for card in cards]
        )

    async def _arun(
        self,
        query: str,
        include_price: bool = False,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""

        payload = {
            "text": query,
            "k": self.k,
            "threshold": self.threshold,
            "lasso_threshold": self.lasso_threshold,
            "sample_results": self.sample_results,
        }
        response = await send_post_request(f"{self.url}cards/", data=payload)
        cards = self._parse_response(response)
        return "\n\n".join(
            [card.to_text(include_price=include_price) for card in cards]
        )

    def _parse_response(self, response: dict) -> list[Card]:
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
        return cards


if __name__ == "__main__":

    card_search = CardSearchTool(url="http://localhost:8000/cards/")

    print(card_search.name)
    print(card_search.description)
    print(card_search.args)
    print(card_search.return_direct)
    print("searching cards.....")
    print("...")
    result = await card_search.arun("chatterfang, squirrel general")
    print(result)

# %%
