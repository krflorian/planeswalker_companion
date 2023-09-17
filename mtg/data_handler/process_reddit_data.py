import re
import json
from pathlib import Path
import pandas as pd


CARD_NAME_PATTERN = r"\[\[.*?\]\]"
BLOCKLIST = ["cardname", "SET"]


def process_reddit_cards_data(
    csv_file: Path = "data/raw/comments/reddit_2019.csv",
) -> list[dict]:
    """Get text and entities from reddit comments.

    Returns:
        [
        {
            "entity": reddit_comment
            "start": start character index of the card name
            "end": end character index of the card name
        }
        ]
    """
    data = pd.read_csv(csv_file)

    documents = []
    for _, row in data.iterrows():
        document = extract_entities_from_text(row["body"])
        if document is not None:
            documents.append(document)

    with open("data/processed/reddit/reddit_2019.json", "w") as outfile:
        json.dump(documents, outfile)

    return documents


def extract_entities_from_text(text):
    """Text with [[card names]] in brackets.

    Subreddit use this patterns for a smart bot that provides links to the cards.
    """
    extracted_cards = []
    for match in re.finditer(CARD_NAME_PATTERN, text):
        card = match.group()
        card = card.replace("[[", "")
        card = card.replace("]]", "")
        extracted_cards.append(card)

    processed_text = text.replace("[[", "")
    processed_text = processed_text.replace("]]", "")

    document = {"text": processed_text, "entities": []}
    try:
        for card in extracted_cards:
            if card not in BLOCKLIST:
                for match in re.finditer(card, processed_text):
                    # print(match.group(), match.start(), match.end())
                    document["entities"].append(
                        {
                            "entity": match.group(),
                            "start": match.start(),
                            "end": match.end(),
                        }
                    )
    except:
        # print("not found", card, processed_text)
        return
    if document["entities"]:
        return document
    return
