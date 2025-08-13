###############################################################################
##  `reader.py`                                                              ##
##                                                                           ##
##  Purpose: Fetches new message events in real time                         ##
###############################################################################


import re
from src.parser import validate_mentions_in_text


# @**First Last (pronoun/pronoun) (batch'year)**
# e.g. @**Adrien Lynch (he/they) (S2'25)**
MENTION_PATTERN = re.compile(
    r"@"
    r"\*\*(?P<name>[^(]+)\s*(\((?P<pronouns>[^)]+)\))?.*?\*\*"
)

def get_mentions(content):
    mentions = []

    for match in MENTION_PATTERN.finditer(content):
        name = match.group("name").strip()
        pronouns = match.group("pronouns")
        
        if pronouns:
            pronouns = pronouns.strip()
            
        mentions.append({"name": name, "pronouns": pronouns})

    return mentions


def scan_for_mentions(content):
    if "@" in content:
        mentions = get_mentions(content)

        for mention in mentions:
            name, pronouns = mention["name"], mention.get("pronouns", "")
            print(f"Name: {name} ... Pronouns: {pronouns}\n")

        results = validate_mentions_in_text(content, mentions)
        print(results)

