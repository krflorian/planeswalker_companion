from pydantic import BaseModel, Field
from typing import Optional


class Rule(BaseModel):
    text: str
    rule_id: str
    chapter: str
    examples: list[str] = Field(default_factory=list)
    subchapter: Optional[str] = None

    def __len__(self):
        return len(self.text)

    @property
    def token_length(self):
        text = self.to_text()

        return len(text.split()) // 2

    def to_text(self):
        text = ""
        if self.chapter:
            text += f"{self.chapter}: "
        if self.subchapter:
            text += self.subchapter
        text += f" {self.rule_id} "
        text += self.text
        if self.examples:
            text += "\nExamples:"
            text += "\n".join(self.examples)
        return text
