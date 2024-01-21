# %%
import spacy
from spacy.language import Language
from spaczz.matcher import FuzzyMatcher
from spacy.tokens import Span, Doc
from spacy.pipeline.functions import merge_entities
from mtg.utils.logging import get_logger

logger = get_logger(__name__)

BLOCK_LIST = [
    "commander",
    "flying",
    "strategy",
    "consider",
    "will",
    "vigilance",
    "lifelink",
    "remove",
    "disrupt",
    "deal damage",
    "sacrifice",
    "sacrificed",
    "persist",
    "battlefield",
    "sorry",
    "flash",
    "X",
    "game",
]

Doc.set_extension("card_names", default=[])


def load_spacy_model(cards: list[str]):
    """loads new spacy model"""
    # load model
    nlp = spacy.blank("en")
    matcher = FuzzyMatcher(nlp.vocab, fuzzy_func="quick", min_r1=80, min_r2=80)

    # set up matcher
    print("setting up matcher...")
    docs = nlp.pipe(cards)
    for doc, card_name in zip(docs, cards):
        card_docs = [doc]
        if "," in card_name:
            short_name = card_name.split(",")[0]
            short_name_doc = nlp(short_name)
            card_docs.append(short_name_doc)
        if "//" in card_name:
            both_sides = card_name.split("//")
            side_docs = nlp.pipe(both_sides)
            card_docs.extend(side_docs)
        matcher.add(card_name, card_docs)

    @Language.component("card_name_matcher")
    def matcher_component(doc):
        matches = matcher(doc)
        entities: list[Span] = []
        logger.info(f"matched {len(matches)} cards: {matches}")
        for card_name, start, end, ratio, pattern in matches:
            if doc[start:end].text.lower() not in BLOCK_LIST:
                entities.append(Span(doc, start, end, card_name))

        doc._.card_names = list(set([entity.label_ for entity in entities]))
        doc.ents = list(spacy.util.filter_spans(entities))
        logger.info(f"added cards: {doc._.card_names}")
        return doc

    nlp.add_pipe("card_name_matcher", last=True)
    nlp.add_pipe("merge_entities", last=True)
    return nlp


def match_cards(text, cards):
    nlp = spacy.blank("en")
    matcher = FuzzyMatcher(nlp.vocab, fuzzy_func="quick", min_r1=80, min_r2=80)

    # add cards to matcher
    docs = nlp.pipe([card.name for card in cards])
    for doc, card in zip(docs, cards):
        card_docs = [doc]
        if "," in card.name:
            short_name = card.name.split(",")[0]
            short_name_doc = nlp(short_name)
            card_docs.append(short_name_doc)
        matcher.add(card.name, card_docs)

    # match cards
    doc = nlp(text)
    matches = matcher(doc)
    entities: list[Span] = []
    for card_name, start, end, ratio, pattern in matches:
        if doc[start:end].text.lower() not in BLOCK_LIST:
            entities.append(Span(doc, start, end, card_name))

    doc._.card_names = list(set([entity.label_ for entity in entities]))
    logger.info(f"matched {len(doc._.card_names)} cards: {doc._.card_names}")
    doc.ents = list(spacy.util.filter_spans(entities))
    doc = merge_entities(doc)
    logger.debug(
        f"adding {len(doc._.card_names)} cards to spacy doc: {doc._.card_names}"
    )

    return doc
