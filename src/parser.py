###############################################################################
##  `parser.py`                                                              ##
##                                                                           ##
##  Purpose: Checks contents of mention in message to validate               ##
###############################################################################


from processing.nlp import PRONOUN_GROUPS
from processing.nlp import get_pronoun_mappings
from processing.llm import validate_pronouns_with_llm

from src.logger import log_debug, log_cluster_mapping, log_validation_results, log_divider


def sanitize_content(content, mentions):
    sanitized = content

    # Replace all name tag instances (full_match) with readable name
    for m in mentions:
        sanitized = sanitized.replace(m.full_match, m.first_name)

    return sanitized


def validate_pronouns_with_nlp(content, mentions):
    pronoun_mappings = get_pronoun_mappings(content, mentions)
    log_cluster_mapping(pronoun_mappings)

    results = []

    for mention in mentions:
        if mention.name not in pronoun_mappings and mention.first_name not in pronoun_mappings:
            continue
        
        clustered_pronouns = pronoun_mappings[mention.first_name]
        
        pronouns = mention.pronouns
        any_allowed = pronouns == () or mention.any_pronouns

        if any_allowed or not clustered_pronouns:
            pronouns_match = True
            mismatches = []
        else:
            # All pronoun forms (specific that person) flattened
            valid_pronouns = [
                form for pronoun in pronouns 
                for form in PRONOUN_GROUPS.get(pronoun, [])
            ]

            # Check for complete match, & record any mismatches 
            pronouns_match = all(p in valid_pronouns for p in clustered_pronouns)
            mismatches = [p for p in clustered_pronouns if p not in valid_pronouns]

        pronouns_display = "/".join(pronouns) if pronouns else "None"
        results.append({
            "name": mention.name,
            "pronouns": pronouns_display,
            "pronouns_match": pronouns_match,
            "mismatches": mismatches
        })

    return results


def validate_mentions_in_text(original_content, mentions):
    # Remove name tags from content text, then apply NLP to extract clusters
    content = sanitize_content(original_content, mentions)

    nlp_results = validate_pronouns_with_nlp(content, mentions)
    log_validation_results(nlp_results, "NLP")

    # Convert list of dicts into a dict keyed by name for easy lookup
    nlp_dict = {r["name"]: r["pronouns_match"] for r in nlp_results}
    nlp_mismatches = {r["name"]: r["mismatches"] for r in nlp_results}

    final_results = []

    for mention in mentions:
        name, pronouns = mention.name, mention.pronouns

        # Check if name was processed by NLP
        nlp_processed = name in nlp_dict
        nlp_match = nlp_dict.get(name, False)
        nlp_mismatch = nlp_mismatches.get(name, False)
        
        # If NLP didn't process this name, default to True (no pronouns used)
        if not nlp_processed:
            pronouns_match = True
        else:
            pronouns_match = nlp_match and not nlp_mismatch # empty mismatch list

        pronouns_display = "/".join(pronouns) if pronouns else "None"
        final_results.append({
            "name": name,
            "pronouns": pronouns_display,
            "pronouns_match": pronouns_match,
            "mismatches": nlp_mismatch
        })

    # log_debug("Combining NLP / LLM results with OR logic")
    log_divider()
    log_debug("Making final determination based on NLP results")

    return final_results



