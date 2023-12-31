import pytest
from pathlib import Path
import pickle
from mtg.data_handler.vector_db import VectorDB


@pytest.fixture(scope="module")
def card_vector_db() -> VectorDB:
    vector_db_file = Path("data/artifacts/card_vector_db.p")

    with vector_db_file.open("rb") as infile:
        card_vector_db: VectorDB = pickle.load(infile)
    return card_vector_db


QUERY_TESTCASES = [
    ("What Cards can i add to my chatterfang deck?", "Chatterfang, Squirrel General"),
    ("Elesh Norn, Mother of Machines", "Elesh Norn, Mother of Machines"),
    ("How does Anje Falkenraths ability work?", "Anje Falkenrath"),
]


@pytest.mark.parametrize("text,expected_card_name", QUERY_TESTCASES)
def test_query(text, expected_card_name, card_vector_db):
    # arrange
    maximum_number_of_results = 5
    maximum_distance = 0.2

    # act
    results = card_vector_db.query(
        text, k=maximum_number_of_results, threshold=maximum_distance
    )

    # assert
    assert len(results) <= maximum_number_of_results
    assert min([r[1] for r in results]) <= maximum_distance
    assert expected_card_name in [r[0] for r in results]
