###############################################################################
##  `parser.py`                                                              ##
##                                                                           ##
##  Purpose: Checks contents of mention in message to validate               ##
###############################################################################


import re 


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

