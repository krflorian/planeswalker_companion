from pathlib import Path
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
    name = "user_deck_lookup"
    description = "Look at decks that the user uploaded"
    args_schema: Type[BaseModel] = DeckSearchInput

    def _run(
        self,
        deck_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""

        filepath = Path(f"data/decks/{deck_name}.txt")
        if not filepath.is_file():
            logger.error(f"did not find deck '{deck_name}'")
            user_decks = "\n".join(
                [
                    file.stem
                    for file in Path(f"data/decks/").iterdir()
                    if file.suffix == ".txt"
                ]
            )
            return f"did not find deck '{deck_name}' - available decks:\n {user_decks}"

        with filepath.open("r", encoding="utf-8") as infile:
            deck = infile.read()
        return deck

    async def _arun(
        self,
        deck_name: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""

        return self._run(deck_name=deck_name, run_manager=run_manager)
