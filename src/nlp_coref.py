###############################################################################
##  `nlp_coref.py`                                                           ##
##                                                                           ##
##  Purpose: Leverages coreference resolution (NLP) for sentence context     ##
###############################################################################


import re
from fastcoref import FCoref
from src.logger import log_info


def apply_nlp(text):
    model = FCoref(device='cpu')  # can use 'cuda:0' for GPU

    preds = model.predict(texts=[text])
    clusters = preds[0].get_clusters()

    return clusters


def extract_name_pronoun_mapping(clusters):
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
    text = (
        "John met Sarah at the cafe. He ordered coffee, and she chose tea. "
        "Sarah thanked him. Later, John waved at her as he left."
        "The two of them had a good time together."
    )

    clusters = apply_nlp(text)
    mappings = extract_name_pronoun_mapping(clusters)

    log_info("Name -> Pronouns Mapping:")

    for name, pronouns in mappings.items():
        log_info(f"  {name}: {pronouns}")
