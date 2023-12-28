import pytest
from pathlib import Path


@pytest.fixture(scope="module")
def card_db() -> CardDB:
    all_cards_file = Path("data/cards/scryfall_all_cards_with_rulings.json")
    vector_db_file = Path("data/artifacts/card_vector_db.p")
    card_db = CardDB(all_cards_file=all_cards_file, vector_db_file=vector_db_file)
    return card_db


QUERY_TESTCASES = [
    (
        """For a Chatterfang, Squirrel General deck, you would want to focus on cards that synergize well with Chatterfang's token-generating ability and its colors, black and green (B/G). Here are three suggestions:

    Deep Forest Hermit - This is a creature that creates Squirrel tokens when it enters the battlefield. It's a green card that fits into Chatterfang’s color identity and synergizes with its ability to double token creation.

    Doubling Season - This is a powerful enchantment that doubles the number of tokens and counters you create. It works incredibly well with Chatterfang's ability to create additional Squirrel tokens.

    Pitiless Plunderer - A creature that can generate additional resources when your creatures die. Since Chatterfang has an ability that requires sacrificing Squirrels, this can provide you with valuable ramp and fixing.

    These cards would all support the token and sacrifice themes in a Chatterfang deck, providing you with both an army of creatures and the resources to utilize Chatterfang's abilities to their fullest. Remember to adjust the deck to your playstyle and the rest of your deck's strategy.""",
        [
            "Chatterfang, Squirrel General",
            "Deep Forest Hermit",
            "Doubling Season",
            "Pitiless Plunderer",
        ],
    ),
    (
        """Tell me 3 cards for my chatterfang commander deck.""",
        [
            "Chatterfang, Squirrel General",
        ],
    ),
    (
        """Tell me 3 cards for my locust god commander deck.""",
        [
            "The Locust God",
        ],
    ),
    (
        """When you attack with Aggressive Mammoth, which is an 8/8 creature with trample, and your opponent blocks it with a 1/1 creature, combat damage is assigned as follows:
        First, you must assign lethal damage to all blockers. In this case, the 1/1 creature blocking the Aggressive Mammoth will be assigned 1 damage, because that is enough to destroy the 1/1 creature (since it is considered lethal damage to a creature with only 1 toughness).
        Then, because Aggressive Mammoth has trample, any remaining damage can be assigned to the defending player or planeswalker that the Mammoth was attacking. Since the Mammoth has 8 power and you are assigning 1 damage to the blocker, the remaining 7 damage goes through to the player or planeswalker.
        Thus, the 1/1 creature would be destroyed, your opponent would take 7 damage, and the Aggressive Mammoth would survive the combat (assuming no other effects, abilities, or damage prevention methods are applied).""",
        ["Aggressive Mammoth"],
    ),
    (
        "Norns decree is on my side and an opponent with 9 poison counters attacks and deals letahl damage to me what happens?",
        ["Norn's Decree"],
    ),
    ("Can I play Vraskas contempt in my opponents turn?", ["Vraska's Contempt"]),
    (
        "how many squirrels does chatterfang create if i tap 5 lands and have Bootlegers Stash on the board?",
        ["Bootleggers' Stash", "Chatterfang, Squirrel General"],
    ),
]


@pytest.mark.parametrize("query,expected_card_names", QUERY_TESTCASES)
def test_card_db_extracts_cards(card_db: CardDB, query, expected_card_names):
    # act
    message = card_db.create_message(
        query,
        role="user",
    )

    # assert
    message_card_names = [card.name for card in message.cards]
    # test precision
    assert len(message.cards) <= len(expected_card_names) + 2
    # test recall
    assert all(
        [card_name in message_card_names for card_name in expected_card_names]
    ), message_card_names
