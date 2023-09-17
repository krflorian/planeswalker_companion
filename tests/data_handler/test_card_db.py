import pytest
from mtg.data_handler import CardDB

db = CardDB("tests/data/cards.json")


CARD_EXTRACTION_TESTCASES = [
    ("What Cards can I add to my Chatterfang Deck?", ["Chatterfang, Squirrel General"]),
    (
        "What Cards can I add to my Schnatterfang, Squirrel General Deck?",
        ["Chatterfang, Squirrel General"],
    ),
    (
        "I'm thinking of making a life drain deck. Nekusar sounds promising but how effective can he be in a 4man pod? What about 1v1?",
        ["Nekusar, the Mindrazer"],
    ),
    (
        "If they were to make a blue version similar to Moonshaker Calvary and Craterhoof Behemeth what other evasive ability do you think would work best? I mean, they could just give it flying again and that'd be cool, but besides that and trample.",
        ["Moonshaker Cavalry", "Craterhoof Behemoth"],
    ),
    (
        "My brother-in-law took this deck apart because it got hated out of every game we played. It was crazy strong, but in a pod, it'd get targeted early, and he'd be a spectator relatively quick. On the flip side, it really taught me the importance of running plenty of interaction",
        [],
    ),
    (
        "For example, if you pass a list or a dict as a parameter value, and the test case code mutates it, the mutations will be reflected in subsequent test case calls.",
        [],
    ),
    ("What is the best flying commander?", []),
]


@pytest.mark.parametrize("text,expected_card_names", CARD_EXTRACTION_TESTCASES)
def test_card_db(text: str, expected_card_names: list[str]):
    doc = db.process_text(text)
    cards = db.extract_card_data_from_doc(doc)

    assert len(cards) == len(expected_card_names)
    for card in cards:
        assert card.name in expected_card_names
