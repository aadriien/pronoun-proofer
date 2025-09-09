###############################################################################
##  `parser.py`                                                              ##
##                                                                           ##
##  Purpose: Checks contents of mention in message to validate               ##
###############################################################################


from src.nlp import PRONOUN_GROUPS
from src.nlp import get_pronoun_mappings
from src.llm import validate_pronouns_with_llm 


def sanitize_content(content, mentions):
    sanitized = content

    # Replace all name tag instances (full_match) with readable name
    for m in mentions:
        sanitized = sanitized.replace(m.full_match, m.name)

    return sanitized


def validate_pronouns_with_nlp(content, mentions):
    pronoun_mappings = get_pronoun_mappings(content, mentions)
    print(f"\n{pronoun_mappings}\n")

    results = []

    for mention in mentions:
        if not mention.name in pronoun_mappings:
            continue
        
        clustered_pronouns = pronoun_mappings[mention.name]
        
        pronouns = mention.pronouns
        any_allowed = pronouns == () or mention.any_pronouns

        if any_allowed or not clustered_pronouns:
            pronouns_match = True
        else:
            # All pronoun forms flattened
            valid_pronouns = [
                form for pronoun in pronouns 
                for form in PRONOUN_GROUPS.get(pronoun, [])
            ]

            pronouns_match = all(p in valid_pronouns for p in clustered_pronouns)

        pronouns_display = "/".join(pronouns) if pronouns else "None"
        results.append({
            "name": mention.name,
            "pronouns": pronouns_display,
            "pronouns_match": pronouns_match
        })

    return results


def validate_mentions_in_text(original_content, mentions):
    # Remove name tags from content text, then apply NLP to extract clusters
    content = sanitize_content(original_content, mentions)
    nlp_results = validate_pronouns_with_nlp(content, mentions)

    # Perform a secondary check with LLM scan
    llm_results = validate_pronouns_with_llm(content, mentions)

    print("\nNLP results:")
    print(nlp_results)

    print("\nLLM results:")
    print(llm_results)


    # Convert list of dicts into a dict keyed by name for easy lookup
    nlp_dict = {r["name"]: r["pronouns_match"] for r in nlp_results}
    llm_dict = {r["name"]: r["pronouns_match"] for r in llm_results}

    # Conservative agreement: True only if both NLP & LLM agree
    final_results = []

    for mention in mentions:
        name, pronouns = mention.name, mention.pronouns

        nlp_match = nlp_dict.get(name, False)
        llm_match = llm_dict.get(name, False)
        
        # OR logic: True if either say True
        pronouns_match_both = nlp_match or llm_match 

        pronouns_display = "/".join(pronouns) if pronouns else "None"
        final_results.append({
            "name": name,
            "pronouns": pronouns_display,
            "pronouns_match": pronouns_match_both
        })

    print("\nFinal conservative results:")
    print(final_results)

    return final_results



