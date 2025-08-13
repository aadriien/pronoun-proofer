###############################################################################
##  `reader.py`                                                              ##
##                                                                           ##
##  Purpose: Fetches new message events in real time                         ##
###############################################################################


from src import parser


def scan_for_mentions(content):
    if "@" in content:
        mentions = parser.parse_mention(content)

        for mention in mentions:
            name, pronouns = mention["name"], mention.get("pronouns", "")
            print(f"Name: {name} ... Pronouns: {pronouns}\n")

        results = parser.validate_mentions_in_text(content, mentions)
        print(results)

