from dataclasses import dataclass, field
from datetime import datetime, timedelta
from mtg.objects import Message


SYSTEM_MESSAGE = """
You are Nissa a Magic the Gathering Assistant, that explains rules, cards and gives advice on playstyles.
Do not answer questions unrelated to Magic the Gathering. If possible explain your answers with the rulings in context.
"""
system_message = Message(SYSTEM_MESSAGE, role="system", processed_text=SYSTEM_MESSAGE)

REMEMBER_TEXT = """
Remember:  You are Nissa a Magic the Gathering Assistant, that explains rules, cards and gives advice on playstyles.
If possible explain your answers with the rulings in context.
Do not answer questions unrelated to Magic the Gathering. Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games. 
"""


@dataclass
class ChatHistory:
    system_message: Message = system_message
    chat: list[Message] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_message(self, message: Message):
        if datetime.now() - self.updated_at > timedelta(minutes=120):
            self.chat = []
        self.chat.append(message)

    def create_prompt(self, number_of_remembered_messages: int = 6):
        prompt = [self.system_message.to_gpt_format()]
        for chat_message in self.chat[-number_of_remembered_messages:]:
            prompt.append(chat_message.to_gpt_format())
        prompt[-1]["content"] = REMEMBER_TEXT + prompt[-1]["content"]
        return prompt

    def create_human_readable_chat(self, number_of_displayed_messages=6):
        chat = []
        for message in self.chat[-number_of_displayed_messages:]:
            if message.role == "user":
                chat.append([message.processed_text])
            if message.role == "assistant":
                chat[-1].append(message.processed_text)

        if len(chat[-1]) == 1:
            chat[-1].append(None)
        return chat
