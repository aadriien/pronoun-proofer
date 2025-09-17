###############################################################################
##  `nlp_spacy.py`                                                           ##
##                                                                           ##
##  Purpose: Leverages coreference resolution (NLP) with spaCy               ##
###############################################################################


import re
import spacy
import json
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logger import log_info, log_original_text


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
    # Load test scenarios from JSON
    scenarios_path = Path(__file__).parent.parent / "examples" / "test_scenarios.json"
    with open(scenarios_path, 'r') as f:
        scenarios = json.load(f)
    
    # Easy swap of category & scenario:
    text = scenarios["multiple_people"]["he_she_conversation"]
    # text = scenarios["edge_cases"]["wrong_pronouns"]
    # text = scenarios["with_mentions"]["complex_scenario"]
    # text = scenarios["neopronouns"]["xe_xem"]
    
    doc = apply_nlp(text)
    
    log_original_text(text)
    
    log_info("Detected clusters:")
    for cluster in doc.spans:
        log_info(f"  {cluster}: {doc.spans[cluster]}")

    mappings = map_names_to_pronouns(doc)

    log_info("Name -> Pronouns Mapping:")
    for name, pronouns in mappings.items():
        log_info(f"  {name}: {pronouns}")


