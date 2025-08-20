###############################################################################
##  `nlp.py`                                                                 ##
##                                                                           ##
##  Purpose: Leverages coreference resolution (NLP) to extract clusters      ##
###############################################################################


import re
import spacy


PRONOUN_GROUPS = {
    "he": ["he", "him", "his", "himself"],
    "she": ["she", "her", "hers", "herself"],
    "they": ["they", "them", "their", "theirs", "themself"],
    "it": ["it", "its", "itself"],
    "xe": ["xe", "xem", "xir", "xyr", "xirs", "xyrs", "xemself"],
    "ze": ["ze", "zir", "hir", "zirs", "hirs", "zirself", "hirself"],
    "fae": ["fae", "faer", "faers", "faerself"],
    "ey": ["ey", "em", "eir", "eirs", "emself"],
}
PRONOUNS = sorted({p for forms in PRONOUN_GROUPS.values() for p in forms})


def apply_nlp(text):
    nlp = spacy.load("en_coreference_web_trf")

    doc = nlp(text)
    return doc


def map_names_to_pronouns(clusters, mentions):
    # Build lookup: full name -> NameTag
    full_name_to_mention = {m.name: m for m in mentions}

    name_to_cluster = {}

    for cluster in clusters:
        cluster_tokens = [t.strip() for t in cluster]

        # Try to match a full name in cluster first
        matched_full_name = None
        for full_name, mention in full_name_to_mention.items():
            if any(
                token == mention.name or token in mention.other_names 
                for token in cluster_tokens
            ):
                matched_full_name = full_name
                break

        main_name = matched_full_name if matched_full_name else cluster_tokens[0]

        # Map main name to everything in cluster (deduplicated)
        existing = set(name_to_cluster.get(main_name, []))
        name_to_cluster[main_name] = list(existing.union(cluster_tokens))

    return name_to_cluster


def get_clusters_from_text(text):
    doc = apply_nlp(text)

    print("\n")
    print(f"Original text input -> {text}\n")

    for cluster in doc.spans:
        print(f"{cluster}: {doc.spans[cluster]}")

    # Build cluster strings
    clusters = []
    
    for cluster in doc.spans:
        cluster_strings = []

        for span in doc.spans[cluster]:
            span_text = doc[span.start : span.end].text  
            cluster_strings.append(span_text)

        if cluster_strings:
            clusters.append(cluster_strings)

    return clusters


def get_pronoun_mappings(text, mentions):
    clusters = get_clusters_from_text(text)
    mappings = map_names_to_pronouns(clusters, mentions)

    print("\nName —> Pronouns Mapping:\n")

    for name, pronouns in mappings.items():
        print(f"{name}: {pronouns}")

    return mappings


