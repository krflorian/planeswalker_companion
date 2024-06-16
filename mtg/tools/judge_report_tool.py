from langchain.tools import BaseTool

from pydantic import BaseModel, Field

from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from mtg.utils.logging import get_logger

logger = get_logger(__name__)


class Source(BaseModel):
    title: str = Field(description="the title of the source")
    url: str = Field(description="the url or link to the source")


class JudgeReport(BaseModel):
    explanation: Optional[str] = Field(
        description="Explanation of why the statement is or is not True according to the sources"
    )
    sources: list[Source] = Field(
        description="list of sources. Every source has a title and a url",
        default_factory=list,
    )


class JudgeReportTool(BaseTool):
    name = "judge_report"
    description = "A structured Report on why a statement is or is not True, with sources and urls for every source"
    args_schema: Type[BaseModel] = JudgeReport

    def _run(
        self,
        explanation: str,
        sources: list[Source] = [],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        print(explanation)
        print("sources:")
        for source in sources:
            print(source.title, source.url)
        if not sources:
            return "No sources added please fill out another report and add sources"
        return "Submitted report"

    async def _arun(
        self,
        explanation: str,
        sources: list[Source] = [],
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs
    ) -> str:
        """Use the tool."""
        return self.run(explanation, sources)
