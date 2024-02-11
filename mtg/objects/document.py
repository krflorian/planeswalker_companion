from pydantic import BaseModel, Field
from typing import Union


class Document(BaseModel):
    name: str  # text for display
    text: str  # text for vectorizing
    url: str  # link to source
    metadata: dict[str, Union[str, list[str]]] = Field(
        default_factory=dict
    )  # more info
    keywords: list[str] = Field(default_factory=list)  # keywords for document

    def __repr__(self):
        return f"Document({self.name})"

    def to_dict(self):
        return self.model_dump()
