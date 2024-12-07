from langchain.tools import BaseTool

from pydantic import BaseModel, Field

from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from mtg.utils.logging import get_logger

logger = get_logger(__name__)


class DeckSearchInput(BaseModel):
    deck_name: str = Field(description="The name of the deck that the user uploaded")


class UserDeckLookupTool(BaseTool):
    name: str = "user_deck_lookup"
    description: str = "Look at decks that the user uploaded"
    args_schema: Type[BaseModel] = DeckSearchInput
    decks: dict[str, str] = {}

    def _run(
        self,
        deck_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""

        deck = self.decks.get(deck_name, None)
        if deck is None:
            deck_list = "\n".join(self.decks.keys())
            logger.error(f"did not find deck '{deck_name}'")
            return f"did not find deck '{deck_name}' - available decks:\n {deck_list}"
        logger.info(f"looked up '{deck_name}' deck")
        return deck

    async def _arun(
        self,
        deck_name: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""

        return self._run(deck_name=deck_name, run_manager=run_manager)
