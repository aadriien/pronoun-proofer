###############################################################################
##  `mentions.py`                                                            ##
##                                                                           ##
##  Purpose: Outlines properties of Zulip name tag for clean validation      ##
###############################################################################


import re
from dataclasses import dataclass, field
from typing import Tuple


# @**First Last (pronoun/pronoun) (batch'year)**
# e.g. @**Adrien Lynch (he/they) (S2'25)**
MENTION_PATTERN = re.compile(
    r"@"
    r"\*\*(?P<content>.*?)\*\*"
)

PAREN_PATTERN = re.compile(r"\(([^)]+)\)")


PRONOUNS_BANK = {
    "he", "him",
    "she", "her",
    "they", "them",
    "it", "its",
    "xe", "xem", "xir",
    "ze", "zir", "hir",
    "fae", "faer",
    "ey", "em", "eir",
}

PRONOUNS_ANY = {
    "any", 
    "all", 
    "indifferent",
}


# Frozen dataclass since fields are immutable
# Note: without specifying `frozen=True`, unhashable type error
@dataclass(frozen=True)
class NameTag:
    full_match: str

    name: str
    name_identifier: str
    first_name: str
    other_names: Tuple[str, ...] = field(default_factory=tuple)

    pronouns: Tuple[str, ...] = field(default_factory=tuple)
    any_pronouns: bool = False
    
    batch_info: Tuple[str, ...] = field(default_factory=tuple)


    @classmethod
    def from_match(cls, match: re.Match) -> "NameTag":
        # Parse full_match @**mention** match into a NameTag instance
        full_match = match.group(0)
        content = match.group("content").strip()

        # Split out parenthetical parts
        parts = PAREN_PATTERN.findall(content)
        base_name = PAREN_PATTERN.split(content)[0].strip()

        pronouns: Tuple[str, ...] = ()
        batch_info: Tuple[str, ...] = ()

        for part in parts:
            # Try to extract any pronouns if they exist (store as collection)
            if cls._looks_like_pronouns(part):
                pronouns = tuple(part.strip().split("/"))
            else:
                batch_info += (part.strip(),)

        name_parts = base_name.strip().split()
        first_name = name_parts[0]
        name_identifier = "_".join(name_parts)
        other_names = tuple(name_parts[1:]) if len(name_parts) > 1 else ()

        any_pronouns = False
        for item in pronouns:
            if item in PRONOUNS_ANY:
                any_pronouns = True
                break

        return cls(
            full_match=full_match,
            name=base_name,
            first_name=first_name,
            name_identifier=name_identifier,
            other_names=other_names,
            pronouns=pronouns,
            any_pronouns=any_pronouns,
            batch_info=batch_info
        )


    @staticmethod
    def _looks_like_pronouns(text: str) -> bool:
        # Check if text looks like valid pronouns
        # - Accepts single known pronouns
        # - Accepts slash-separated forms like 'he/they'
        # - Accepts special descriptors like 'indifferent'
        lowered = text.strip().lower()

        if lowered in PRONOUNS_ANY:
            return True

        parts = lowered.split("/")
        return all(part in PRONOUNS_BANK for part in parts)


def get_mentions(content: str):
    all_mentions = [NameTag.from_match(m) for m in MENTION_PATTERN.finditer(content)]
    unique_mentions = set(all_mentions)
    
    return list(unique_mentions)





###############################################################################
##  PROPERTY NOTES                                                           ##
##                                                                           ##
##  Assumption x Behavior x Rationale                                        ##
###############################################################################

# Assumption: 
#   - message mentions single person (known pronouns)
#   - person referenced later in message
# Behavior: 
#   - bot can create Mention class instance (from name + pronouns)


# Assumption: 
#   - we have data structures with all pieces
#   - correct pronouns
# Behavior: 
#   - do nothing! :D

# Assumption: 
#   - we have data structures with all pieces
#   - mismatch of pronouns
# Behavior: 
#   - do something! :D
#   - indicate mismatch as response
#   - action steps triggered by mismatch 


### DATA STRUCTURES ###

# Sum type? Can reference by name, any viable pronouns
#   - also sum type: reference by first name? last name? full name?
#   - also sum type: reference by one pronoun? many?


# viola he (they) (...)
#   - entity / identity: "viola he"
#   - reference: they
# Expected Behavior: nothing

# viola he (they) (...)
#   - entity / identity: "viola he"
#   - reference: they
# Expected Behavior: nothing

# viola he (they) (...)
#   - entity / identity: "viola he"
#   - reference: he
# Expected Behavior: something (mismatch response data)


# Note for future: revisit Lauria as TC for last name edge case


