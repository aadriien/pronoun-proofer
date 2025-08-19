###############################################################################
##  `reader.py`                                                              ##
##                                                                           ##
##  Purpose: Fetches new message events in real time                         ##
###############################################################################


from src.mentions import get_mentions
from src.parser import validate_mentions_in_text
from src.notifier import notify_writer_of_mismatch


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

