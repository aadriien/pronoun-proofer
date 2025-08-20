###############################################################################
##  `nlp_spacy.py`                                                           ##
##                                                                           ##
##  Purpose: Leverages coreference resolution (NLP) with spaCy               ##
###############################################################################


import re
import spacy
from pathlib import Path


def apply_nlp(text):
    # Use fine-tuned model that recognizes neopronouns!
    base = Path(__file__).resolve().parent.parent   # project root
    # nlp = spacy.load(base / "coref" / "training" / "coref")

    # nlp = spacy.load(base / "coref" / "training" / "finetune_cluster" / "model-best")
    
    # Fallback to original model if fine-tuned model not found
    nlp = spacy.load("en_coreference_web_trf")

    doc = nlp(text)

    return doc


def map_names_to_pronouns(doc):
    clusters = []

    for cluster in doc.spans:
        cluster_strings = []
        for span in doc.spans[cluster]:
            # Handle single-token spans where start == end
            if span.start < len(doc):
                token = doc[span.start]
                cluster_strings.append(token.text)
        if cluster_strings:  # Only add non-empty clusters
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

    # text = (
    #     "John met Sarah at the cafe. He ordered coffee, and she chose tea. "
    #     "Sarah thanked him. Later, John waved at her as he left. "
    #     "The two of them had a good time together."
    # )

    # text = (
    #     "John met Sarah at the cafe. He ordered coffee, and ze chose tea. "
    #     "Sarah's tea was very hot, but ze enjoyed zir tea. "
    #     "Sarah thanked him. Later, John waved at zir as he left. "
    #     "The two of them had a good time together."
    # )

    # text = (
    #     "I met with with @**John Smith (he/they) (S2'25)** today. "
    #     "He showed me what he was working on."
    # )

    # text = (
    #     "I met with with @**John Smith (he/they) (S2'25)** today. "
    #     "They showed me what they were working on."
    # )

    text = (
        "I met with with @**Viola He (they) (S2'25)** today. "
        "They showed me what they were working on. "
        "Viola's work is really cool. I love seeing their projects."
        "I also worked with @**K Lauria (he) (S2'25)**. "
        "His ideas were great. Lauria has so many cool ideas."
    )

    # text = (
    #     "I paired with with @**Alex Lee (he) (S2'25)** today. "
    #     "Alex showed me his code, and I enjoyed working with him. "
    #     "@**Alex Brown (she) (S2'25)** joined us later on. "
    #     "She shared a bunch of ideas."
    # )

    # text = (
    #     "I paired with with Alex Lee today. "
    #     "Alex showed me his code, and I enjoyed working with him. "
    #     "Alex Brown joined us later on. "
    #     "She shared a bunch of ideas."
    # )

    # text = (
    #     "I paired with with Alex_Lee today. "
    #     "Alex showed me his code, and I enjoyed working with him. "
    #     "Alex_Brown (she/her, S2'25) joined us later on. "
    #     "She shared a bunch of ideas."
    # )

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


