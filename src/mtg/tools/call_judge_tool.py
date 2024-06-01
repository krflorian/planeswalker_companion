from langchain.tools import BaseTool

from pydantic import BaseModel, Field

from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from mtg.utils.logging import get_logger

logger = get_logger(__name__)


class CallJudgeInput(BaseModel):
    question: Optional[str] = Field(
        default=None, description="Specific question for the judge"
    )


class CallJudgeTool(BaseTool):
    name = "call_mtg_judge"
    description = "Calls a judge that double checks rulings. Judge must be called in case the user asks rules questions"
    question: str = None
    args_schema: Type[BaseModel] = CallJudgeInput
    is_called: bool = False

    def _run(
        self,
        question: str = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""

        self.question = question
        return (
            "A Magic the Gathering Judge will double check your response to the user."
        )

    async def _arun(
        self,
        question: str = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""

        return self._run(question=question, run_manager=run_manager)
