###############################################################################
##  `reader.py`                                                              ##
##                                                                           ##
##  Purpose: Fetches new message events in real time                         ##
###############################################################################


import re
from src.parser import validate_mentions_in_text
from src.notifier import notify_writer_of_mismatch


# @**First Last (pronoun/pronoun) (batch'year)**
# e.g. @**Adrien Lynch (he/they) (S2'25)**
MENTION_PATTERN = re.compile(
    r"@"
    r"\*\*(?P<name>[^(]+)\s*(\((?P<pronouns>[^)]+)\))?.*?\*\*"
)

def get_mentions(content):
    mentions = []

    for match in MENTION_PATTERN.finditer(content):
        full_match = match.group(0)
        name = match.group("name").strip()
        pronouns = match.group("pronouns")
        
        if pronouns:
            pronouns = pronouns.strip()
            
        mentions.append({
            "full_match": full_match,
            "name": name, 
            "pronouns": pronouns
        })

    return mentions


def scan_for_mentions(message, client):
    content = message["content"]

    if "@" in content:
        mentions = get_mentions(content)

        for mention in mentions:
            full_match = mention["full_match"]
            name = mention["name"]
            pronouns =  mention.get("pronouns", "")
            
            print(f"Full Match: {full_match} ... Name: {name} ... Pronouns: {pronouns}\n")

        results = validate_mentions_in_text(content, mentions)
        for r in results:
            print(f"Name: {r['name']}")
            print(f"Pronouns: {r['pronouns']}")
            print(f"Positions: {r['positions']}")
            print("Checks:")
            for i, check in enumerate(r["checks"], 1):
                print(f"  Check {i}:")
                print(f"    Snippet: {check['snippet']!r}")
                print(f"    Pronouns match: {check['pronouns_match']}")
            print("-" * 50)

        for r in results:
            if not all(check["pronouns_match"] for check in r["checks"]):
                notify_writer_of_mismatch(message, r, client)

