import spacy
from spacy.language import Language
from spaczz.matcher import FuzzyMatcher
from spacy.tokens import Span
import logging

BLOCK_LIST = [
    "commander",
    "flying",
    "strategy",
    "consider",
    "will",
    "vigilance",
    "remove",
    "disrupt",
    "deal damage",
    "sacrifice",
    "battlefield",
]


def load_spacy_model(model_name: str, all_cards: list[str]):
    """loads new spacy model"""
    # load model
    nlp = spacy.load(model_name)
    matcher = FuzzyMatcher(nlp.vocab)

    # set up matcher
    print("setting up matcher...")
    docs = nlp.pipe(all_cards)
    for doc, card_name in zip(docs, all_cards):
        docs = [doc]
        if "," in card_name:
            short_name = card_name.split(",")[0]
            short_name_doc = nlp(short_name)
            docs.append(short_name_doc)
        if "//" in card_name:
            both_sides = card_name.split("//")
            side_docs = nlp.pipe(both_sides)
            docs.extend(side_docs)
        matcher.add(card_name, docs)

    @Language.component("card_name_matcher")
    def matcher_component(doc):
        matches = matcher(doc)
        entities = []
        for card_name, start, end, ratio, pattern in matches:
            if ratio > 93 and (doc[start:end].text.lower() not in BLOCK_LIST):
                logging.info(
                    f"adding card data for {card_name}, similarity {ratio}, text {doc[start:end]}"
                )
                entities.append(Span(doc, start, end, card_name))
        doc.ents = list(spacy.util.filter_spans(entities))
        return doc

    nlp.add_pipe("card_name_matcher", last=True)
    nlp.add_pipe("merge_entities", last=True)
    return nlp
