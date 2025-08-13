###############################################################################
##  `test_reader.py`                                                         ##
##                                                                           ##
##  Purpose: Tests extraction of name & pronouns from text                   ##
###############################################################################


import pytest
from src import reader


# -----------------------------
# Single pronouns
# -----------------------------
def test_single_pronoun_she():
    content = "@**Alice Smith (she/her) (SP1'25)** is coding"
    mentions = reader.get_mentions(content)

    assert mentions[0]["name"] == "Alice Smith"
    assert mentions[0]["pronouns"] == "she/her"


def test_single_pronoun_he():
    content = "@**Bob Jones (he/him) (F2'24)** finished the task"
    mentions = reader.get_mentions(content)

    assert mentions[0]["name"] == "Bob Jones"
    assert mentions[0]["pronouns"] == "he/him"


def test_single_pronoun_they():
    content = "@**Charlie (they/them) (F1'23)**"
    mentions = reader.get_mentions(content)

    assert mentions[0]["name"] == "Charlie"
    assert mentions[0]["pronouns"] == "they/them"


# -----------------------------
# Multiple pronouns
# -----------------------------
def test_multiple_pronouns():
    content = "@**Dana Lee (she/they) (F1'24)** paired with @**Elliot Kim (he/they) (F2'25)**"
    mentions = reader.get_mentions(content)
    
    assert mentions[0]["name"] == "Dana Lee"
    assert mentions[0]["pronouns"] == "she/they"
    assert mentions[1]["name"] == "Elliot Kim"
    assert mentions[1]["pronouns"] == "he/they"


# -----------------------------
# No pronouns
# -----------------------------
def test_no_pronouns():
    content = "@**Frank Liu (W1'19)** joined the chat"
    mentions = reader.get_mentions(content)
    assert mentions[0]["name"] == "Frank Liu"
    assert mentions[0].get("pronouns") is None


# -----------------------------
# Neopronouns
# -----------------------------
def test_neopronouns_single():
    content = "@**Gale Xy (ze/zir) (S2'15)** commented"
    mentions = reader.get_mentions(content)
    assert mentions[0]["name"] == "Gale Xy"
    assert mentions[0]["pronouns"] == "ze/zir"


def test_neopronouns_multiple():
    content = "@**Harper Q (xe/xem) (F2'20)** and @**Indi Y (ey/em) (F1'25)** paired up"
    mentions = reader.get_mentions(content)

    assert mentions[0]["name"] == "Harper Q"
    assert mentions[0]["pronouns"] == "xe/xem"
    assert mentions[1]["name"] == "Indi Y"
    assert mentions[1]["pronouns"] == "ey/em"


# -----------------------------
# No mentions
# -----------------------------
def test_no_mentions():
    content = "No mentions here"
    mentions = reader.get_mentions(content)
    assert mentions == []


# -----------------------------
# Any pronouns
# -----------------------------
def test_no_pronouns():
    content = "@**Micah (any) (W2'15)** had a really cool idea"
    mentions = reader.get_mentions(content)

    assert mentions[0]["name"] == "Micah"
    assert mentions[0]["pronouns"] == "any"


