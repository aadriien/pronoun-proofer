###############################################################################
##  `parser.py`                                                              ##
##                                                                           ##
##  Purpose: Checks contents of mention in message to validate               ##
###############################################################################


import re 


PRONOUNS_BANK = [
    "he", "him", "his", "himself",
    "she", "her", "hers", "herself",
    "they", "them", "their", "theirs", "themself",
    "xe", "xem", "xyr", "xyrs", "xemself",
    "ze", "hir", "hirs", "hirself",
]

# @**First Last (pronoun/pronoun) (batch'year)**
# e.g. @**Adrien Lynch (he/they) (S2'25)**
MENTION_PATTERN = re.compile(
    r"@"
    r"\*\*(?P<name>[^(]+)\s*(\((?P<pronouns>[^)]+)\))?.*?\*\*"
)

def parse_mention(content):
    mentions = []

    for match in MENTION_PATTERN.finditer(content):
        name = match.group("name").strip()
        pronouns = match.group("pronouns")
        
        if pronouns:
            pronouns = pronouns.strip()
            
        mentions.append({"name": name, "pronouns": pronouns})

    return mentions


def validate_mentions_in_text(content, mentions):
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
    nearby_checks = []

    for pos in positions:
        # 50 chars before / after
        window_start = max(0, pos - 50) 
        window_end = min(len(content), pos + 50) 
        snippet = content[window_start:window_end]
        
        # If no known pronouns in text block, consider it a match
        pronouns_present = any(p in snippet for p in PRONOUNS_BANK)
        if not pronouns_present:
            pronouns_match = True
        else:
            # Otherwise, check if any expected pronouns in snippet
            pronouns_match = all(
                p.strip().lower() in snippet for p in pronouns.split("/")
            ) if pronouns else True

        nearby_checks.append({
            "snippet": snippet,
            "pronouns_match": pronouns_match
        })

    return nearby_checks

