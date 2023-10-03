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
For every user question first give a short summary of the answer then, if possible explain your summary with the rulings and card data in context.
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

    def create_prompt(self, number_of_remembered_messages: int = 4):
        # TODO dynamic prompt length (max 4097 tokens)
        prompt = [self.system_message.to_gpt_format()]
        for chat_message in self.chat[-number_of_remembered_messages:]:
            prompt.append(chat_message.to_gpt_format())
        prompt[-1]["content"] = REMEMBER_TEXT + prompt[-1]["content"]
        return prompt

    def create_human_readable_chat(self, number_of_displayed_messages=4):
        """Create Chat for display in gradio bot.

        Chat has to be in format list of lists. First message in the list is user second is bot.
        Example:
        chat = [[user, bot], [user, bot]]
        """
        chat = []
        for message in self.chat[-number_of_displayed_messages:]:
            if message.role == "user":
                chat.append([message.processed_text])
            if message.role == "assistant":
                if not chat:
                    chat.append([None, message.processed_text])
                else:
                    chat[-1].append(message.processed_text)

        if len(chat[-1]) == 1:
            chat[-1].append(None)
        return chat
