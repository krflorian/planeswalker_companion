from langchain.tools import BaseTool

from pydantic import BaseModel, Field, field_validator

from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from mtg.utils.logging import get_logger

logger = get_logger(__name__)


class Source(BaseModel):
    title: str = Field(
        description="The title of the source where the information in explanation comes from"
    )
    url: str = Field(description="The url or link to the source")


class JudgeReport(BaseModel):
    explanation: str = Field(
        description="Explanation of why the statement is or is not True according to the sources"
    )
    sources: list[Source] = Field(
        description="List your Sources here.", default_factory=list
    )


class JudgeReportTool(BaseTool):
    name = "judge_report"
    description = "A structured Report on why a statement is or is not True, with sources and urls for the explanation."
    args_schema: Type[BaseModel] = JudgeReport

    def _run(
        self,
        explanation: str,
        sources: list[Source] = [],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""

        logger.info(f"submitting judge report with {len(sources)} sources")
        if not sources:
            print("explanation: ", explanation)
            print("sources:", sources)
            return "No sources added. Please fill out another report and add sources."
        return "Successfully Submitted report"

    async def _arun(
        self,
        explanation: str,
        sources: list[Source] = [],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        **kwargs,
    ) -> str:
        """Use the tool."""
        return self._run(
            explanation=explanation, sources=sources, run_manager=run_manager
        )
