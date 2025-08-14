###############################################################################
##  `parser.py`                                                              ##
##                                                                           ##
##  Purpose: Checks contents of mention in message to validate               ##
###############################################################################


import re 


PRONOUN_GROUPS = {
    "he": ["he", "him", "his", "himself"],
    "she": ["she", "her", "hers", "herself"],
    "they": ["they", "them", "their", "theirs", "themself"],
    "xe": ["xe", "xem", "xyr", "xyrs", "xemself"],
    "ze": ["ze", "hir", "hirs", "hirself"],
}
ALL_PRONOUNS = sorted({p for forms in PRONOUN_GROUPS.values() for p in forms})


def sanitize_content(content, mentions):
    sanitized = content

    # Remove exact full name mention from content
    for m in mentions:
        full_match = re.escape(m["full_match"])
        sanitized = re.sub(rf'\(\s*{re.escape(m["pronouns"])}\s*\)', '', sanitized)

    return sanitized


def validate_mentions_in_text(original_content, mentions):
    # Remove name tags from content text for easier validation later
    content = sanitize_content(original_content, mentions)
    results = []

    for mention in mentions:
        # Name stored in full, so extract only first name to find in text
        full_name = mention["name"].strip().split()
        name = full_name[0]
        positions = find_all_name_appearances(content, name)

        # Simple check to see if pronouns occur near the name
        pronouns = mention.get("pronouns", "") 
        pronoun_checks = check_nearby_pronouns(content, pronouns, positions)

        results.append({
            "name": name,
            "pronouns": pronouns,
            "positions": positions,
            "checks": pronoun_checks
        })

    return results


def find_all_name_appearances(content, name):
    content_lower = content.lower()
    name_lower = name.lower()

    positions = []
    start = 0

    while True:
        idx = content_lower.find(name_lower, start)
        if idx == -1:
            break
        positions.append(idx)
        start = idx + len(name_lower) 

    return positions


def check_nearby_pronouns(content, pronouns, positions):
    if not positions:
        return [{"snippet": "", "pronouns_match": True}]
    
    nearby_checks = []

    if pronouns:
        pronouns_list = []
        for p in pronouns.split("/"):
            p = p.lower()
            pronouns_list.extend(PRONOUN_GROUPS.get(p, [p]))
    else:
        pronouns_list = []

    for pos in positions:
        # 50 chars before / after
        window_start = max(0, pos - 50)
        window_end = min(len(content), pos + 50)
        snippet = content[window_start:window_end].lower()

        # Extract all pronouns in snippet
        snippet_pronouns = [p for p in ALL_PRONOUNS if re.search(rf'\b{p}\b', snippet)]

        if not pronouns_list or "any" in pronouns_list or "indifferent" in pronouns_list:
            pronouns_match = True

        elif not snippet_pronouns:
            pronouns_match = True 

        else:
            # Ensure pronouns in snippet match person's viable pronouns
            pronouns_match = any(p in pronouns_list for p in snippet_pronouns)

        nearby_checks.append({
            "snippet": snippet,
            "pronouns_match": pronouns_match
        })

    return nearby_checks

