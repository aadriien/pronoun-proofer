###############################################################################
##  `nlp_spacy.py`                                                           ##
##                                                                           ##
##  Purpose: Leverages coreference resolution (NLP) with spaCy               ##
###############################################################################


import re
import spacy


def apply_nlp(text):
    nlp = spacy.load("en_coreference_web_trf")
    doc = nlp(text)

    return doc


def map_names_to_pronouns(doc):
    clusters = []

    for cluster in doc.spans:
        cluster_strings = [span.text for span in doc.spans[cluster]]
        clusters.append(cluster_strings)


    pronouns = {"he", "him", "his", "she", "her", "hers", "they", "them", "their", "theirs"}
    name_to_pronouns = {}

    for cluster in clusters:
        # Prefer proper name over pronouns
        name_candidates = [m for m in cluster if re.match(r"^[A-Z][a-z]+$", m) and m.lower() not in pronouns]
        if name_candidates:
            # Choose longest name candidate
            main_name = max(name_candidates, key=len)
        else:
            # Fall back to first mention in cluster
            main_name = cluster[0]

        cluster_pronouns = [m for m in cluster if m.lower() in pronouns]
        if cluster_pronouns:
            name_to_pronouns[main_name] = cluster_pronouns

    return name_to_pronouns


if __name__ == "__main__":
    # text = (
    #     "Philip plays the bass because he loves it."
    # )

    # text = (
    #     "Sarah enjoys a nice cup of tea in the morning. She likes it with sugar and a drop of milk."
    # )

    text = (
        "John met Sarah at the cafe. He ordered coffee, and she chose tea. "
        "Sarah thanked him. Later, John waved at her as he left. "
        "The two of them had a good time together."
    )

    # text = (
    #     "The group had fun. They discussed many things."
    # )

    # text = (
    #     "Alice and Bob had fun. They discussed many things."
    # )

    # text = (
    #     "Alice and Bob said they like cheese, but he prefers sushi."
    # )

    # text = (
    #     "Sarah showed me his code."
    # )

    # text = (
    #     "Sarah showed me xyr code."
    # )



    # import torch
    # print(torch.backends.mps.is_available())   # True means MPS is usable
    # print(torch.backends.mps.is_built())       # True means MPS was built into torch

    # import spacy
    # from thinc.api import prefer_gpu

    # print(prefer_gpu())  # True if spaCy can use GPU/MPS



    doc = apply_nlp(text)

    print("\n")
    print(f"Original text input -> {text}\n")

    # print(doc.spans)

    for cluster in doc.spans:
        print(f"{cluster}: {doc.spans[cluster]}")

    mappings = map_names_to_pronouns(doc)

    print("\nName —> Pronouns Mapping:\n")

    for name, pronouns in mappings.items():
        print(f"{name}: {pronouns}")


