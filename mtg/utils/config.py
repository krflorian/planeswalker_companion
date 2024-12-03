import os
from pathlib import Path
import yaml
from pydantic import BaseModel, Field
from functools import cache


class LLMSettings(BaseModel):
    open_ai_token: str
    llm_model_version: str = Field(
        default="gpt-4o", description="openai model version powering the agents"
    )


class LangfuseSettings(BaseModel):
    secret_key: str
    public_key: str
    host: str


class DataserviceSettings(BaseModel):
    host: str = Field(
        default="http://localhost:8000/", description="Url for the dataservice server."
    )
    card_search_number_of_cards: int = Field(
        default=20,
        description="threshold for the number of cards that will be returned by card search",
    )
    card_search_threshold: float = Field(
        default=0.5,
        description="threshold for the similarity to the search query for card search",
    )
    rules_search_threshold: float = Field(
        default=0.75,
        description="threshold for the similarity to the search query for rules search",
    )


class MTGBotConfig(BaseModel):
    dataservice_settings: DataserviceSettings
    llm_settings: LLMSettings
    langfuse_settings: LangfuseSettings


@cache
def load_config(filepath: Path) -> MTGBotConfig:
    filepath = Path(filepath)

    with filepath.open("r") as infile:
        config = yaml.safe_load(infile)

    config = MTGBotConfig(**config)
    os.environ["OPENAI_API_KEY"] = config.llm_settings.open_ai_token
    os.environ["LANGFUSE_PUBLIC_KEY"] = config.langfuse_settings.public_key
    os.environ["LANGFUSE_SECRET_KEY"] = config.langfuse_settings.secret_key
    os.environ["LANGFUSE_HOST"] = config.langfuse_settings.host

    return config
