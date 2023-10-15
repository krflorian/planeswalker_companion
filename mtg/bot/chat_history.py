from dataclasses import dataclass, field
from mtg.objects import Message


@dataclass
class ChatHistory:
    chat: list[Message] = field(default_factory=list)

    def add_message(self, message: Message):
        self.chat.append(message)

    def get_card_data(self, number_of_messages=2):
        """Get Card data from last n messages in text form."""
        card_data = ""
        for message in self.chat[-number_of_messages:]:
            card_data += "\n".join([card.to_text() for card in message.cards])
        if card_data == "":
            card_data = "No Card Data."
        return card_data

    def get_human_readable_chat(self, number_of_messages=4):
        """Create Chat for display in gradio bot.

        Chat has to be in format list of lists. First message in the list is user second is bot.
        Example:
        chat = [[user, bot], [user, bot]]
        """
        chat = []
        for message in self.chat[-number_of_messages:]:
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
