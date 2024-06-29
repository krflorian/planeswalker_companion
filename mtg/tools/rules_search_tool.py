import aiohttp
import requests
from langchain.tools import BaseTool

from pydantic import BaseModel, Field

from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from mtg.objects import Document
from mtg.utils.logging import get_logger

logger = get_logger(__name__)


async def send_post_request(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            response_json = await response.json()
            return response_json


class RulesSearchInput(BaseModel):
    query: str = Field(
        description="should be a search. can also be a paragraph of a rule from comprehensive rules."
    )


class RulesSearchTool(BaseTool):
    name = "mtg_rules_search"
    args_schema: Type[BaseModel] = RulesSearchInput
    url: str = "http://localhost:8000/"
    k: int = 10
    threshold: float = 0.4
    lasso_threshold: float = 0.2
    description = """
    Lookup Magic the Gathering rules and information about various keywords from trustworthy sources:
        - Comprehensive Rulebook
        - Rulesguru.com
        - Stackexchange
        - Wikipedia.
    """

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""

        logger.info(f"Triggering Rules Search with query: {query}")

        response = requests.post(
            url=f"{self.url}rules/",
            json={
                "text": query,
                "k": self.k,
                "threshold": self.threshold,
                "lasso_threshold": self.lasso_threshold,
            },
        )
        response = response.json()
        return self._parse_response(response)

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""

        logger.info(f"Triggering Rules Search with query: {query}")

        payload = {
            "text": query,
            "k": self.k,
            "threshold": self.threshold,
            "lasso_threshold": self.lasso_threshold,
        }
        response = await send_post_request(f"{self.url}rules/", data=payload)
        return self._parse_response(response)

    def _parse_response(self, response: dict) -> list[Document]:
        """parses response to string and saves documents in history"""
        documents = []
        for resp in response:
            document = resp["document"]
            distance = resp["distance"]
            document = Document(**document)
            documents.append(document)
            logger.debug(f"received document {document.name} distance {distance:.2f}")

        logger.info(f"received {len(documents)} documents from rules search tool")

        origin_2_doc = {}
        for doc in documents:
            origin = doc.metadata.get("origin", "other rules:")
            if origin not in origin_2_doc:
                origin_2_doc[origin] = []
            text = f"{doc.name} - {doc.text}\nsource: {doc.url}"
            origin_2_doc[origin].append(text)

        # merge texts
        rule_texts = ""
        for origin, texts in origin_2_doc.items():
            rule_texts += origin + ":\n"
            for text in texts:
                rule_texts += f"{text}\n\n"
        if rule_texts:
            return rule_texts
        else:
            return "No Rules found"
