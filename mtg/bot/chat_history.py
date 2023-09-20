SYSTEM_MESSAGE = """
You are Nissa a Magic the Gathering Assistant, that explains rules, cards and gives advice on playstyles.
Do not answer questions unrelated to Magic the Gathering. If possible explain your answers with the rulings in context.
"""

REMEMBER_MESSAGE = """
Remember:  You are Nissa a Magic the Gathering Assistant, that explains rules, cards and gives advice on playstyles.
If possible explain your answers with the rulings in context.
Do not answer questions unrelated to Magic the Gathering. Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games. 
"""


# %%
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from mtg.objects import Card


@dataclass
class Message:
    text: str
    role: str
    processed_text: str
    cards: list[Card] = field(default_factory=list)

    def to_gpt_format(self) -> dict:
        content = ""
        if self.cards:
            cards_context = "\n".join([card.to_text() for card in self.cards])
            content += f"CONTEXT: \n{cards_context}\n\n"
        content += f"\n{self.text}"
        return {"role": self.role, "content": content}


@dataclass
class ChatHistory:
    system_message: Message = Message(
        SYSTEM_MESSAGE, role="system", processed_text=SYSTEM_MESSAGE
    )
    remember_string: str = REMEMBER_MESSAGE
    chat: list[Message] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)

    def create_prompt(self, number_of_remembered_messages: int = 4):
        prompt = [self.system_message.to_gpt_format()]
        for chat_message in self.chat[-number_of_remembered_messages:]:
            prompt.append(chat_message.to_gpt_format())
        prompt[-1]["content"] = self.remember_string + prompt[-1]["content"]
        return prompt

    def add_message(self, text: str, role: str, cards: list[Card], processed_text: str):
        if datetime.now() - self.updated_at > timedelta(minutes=120):
            self.chat = []
        message = Message(
            text=text, role=role, cards=cards, processed_text=processed_text
        )
        self.chat.append(message)

    def create_human_readable_chat(self, number_of_displayed_messages=4):
        chat = []
        for message in self.chat[-number_of_displayed_messages:]:
            if message.role == "user":
                chat.append([message.processed_text])
            if message.role == "assistant":
                chat[-1].append(message.processed_text)

        if len(chat[-1]) == 1:
            chat[-1].append(None)
        return chat
