# %%
import spacy
from spacy.language import Language
from spaczz.matcher import FuzzyMatcher
from spacy.tokens import Span, Doc
import logging

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
]

Doc.set_extension("card_names", default=[])


def load_spacy_model(all_cards: list[str]):
    """loads new spacy model"""
    # load model
    nlp = spacy.blank("en")
    matcher = FuzzyMatcher(nlp.vocab, fuzzy_func="quick", min_r1=93, min_r2=93)

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
        entities: list[Span] = []
        logging.info(f"matched {len(matches)} cards: {matches}")
        for card_name, start, end, ratio, pattern in matches:
            if doc[start:end].text.lower() not in BLOCK_LIST:
                entities.append(Span(doc, start, end, card_name))

        doc._.card_names = list(set([entity.label_ for entity in entities]))
        doc.ents = list(spacy.util.filter_spans(entities))
        logging.info(f"added cards: {doc._.card_names}")
        return doc

    nlp.add_pipe("card_name_matcher", last=True)
    nlp.add_pipe("merge_entities", last=True)
    return nlp
