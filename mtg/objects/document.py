from pydantic import BaseModel, Field


class Document(BaseModel):
    name: str  # text for display
    text: str  # text for vectorizing
    url: str  # link to source
    metadata: dict[str, str] = Field(default_factory=dict)  # more info
    keywords: list[str] = Field(default_factory=list)  # keywords for document

    def __repr__(self):
        return f"Document({self.name})"
