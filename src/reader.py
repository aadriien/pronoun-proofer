###############################################################################
##  `reader.py`                                                              ##
##                                                                           ##
##  Purpose: Fetches new message events in real time                         ##
###############################################################################


import sys 

from src.mentions import get_mentions
from src.parser import validate_mentions_in_text
from src.notifier import notify_writer_of_mismatch


def scan_for_mentions(message, client):
    content = message["content"]

    if "@" in content:
        mentions = get_mentions(content)

        for mention in mentions:
            full_match = mention.full_match
            name = mention.name
            pronouns =  mention.pronouns
            
            pronouns_display = "/".join(pronouns) if pronouns else "None"
            print(f"Full Match: {full_match} ... Name: {name} ... Pronouns: {pronouns_display}\n")


        results = validate_mentions_in_text(content, mentions)
        for r in results:
            print(f"\nName: {r['name']}")
            print(f"Pronouns: {r['pronouns']}")
            print(f"Pronouns match: {r['pronouns_match']}")
            

        for r in results:
            if not r['pronouns_match']:
                notify_writer_of_mismatch(message, r, client)

        sys.stdout.flush()

