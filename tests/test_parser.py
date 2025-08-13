###############################################################################
##  `test_parser.py`                                                         ##
##                                                                           ##
##  Purpose: Tests validation of name & pronouns in text                     ##
###############################################################################


import pytest
from src import parser

# -----------------------------
# Single pronouns
# -----------------------------
def test_single_pronoun_she_nearby():
    content = "Alice is coding. She is doing well."
    mentions = [{
        "full_match": "@**Alice Smith (she/her) (SP1'25)**",
        "name": "Alice Smith",
        "pronouns": "she/her"
    }]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_single_pronoun_he_nearby():
    content = "Bob finished the task. He did it quickly."
    mentions = [{
        "full_match": "@**Bob Jones (he/him) (F2'24)**",
        "name": "Bob Jones",
        "pronouns": "he/him"
    }]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_single_pronoun_they_not_nearby():
    content = "Charlie said she is busy."
    mentions = [{
        "full_match": "@**Charlie (they/them) (F1'23)**",
        "name": "Charlie",
        "pronouns": "they/them"
    }]

    results = parser.validate_mentions_in_text(content, mentions)
    assert not all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# Multiple pronouns
# -----------------------------
def test_multiple_pronouns_match():
    content = "Dana shared her notes. Elliot did his part."
    mentions = [
        {
            "full_match": "@**Dana Lee (she/they) (F1'24)**", 
            "name": "Dana Lee", 
            "pronouns": "she/they"
        },
        {
            "full_match": "@**Elliot Kim (he/they) (F2'25)**", 
            "name": "Elliot Kim", 
            "pronouns": "he/they"
        }
    ]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_multiple_pronouns_partial_match():
    content = "Dana used they pronouns. Elliot prefers he/him."
    mentions = [
        {
            "full_match": "@**Dana Lee (she/they) (F1'24)**", 
            "name": "Dana Lee", 
            "pronouns": "she/they"
        },
        {
            "full_match": "@**Elliot Kim (he/they) (F2'25)**", 
            "name": "Elliot Kim", 
            "pronouns": "he/they"
        }
    ]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# No pronouns
# -----------------------------
def test_no_pronouns_in_tag():
    content = "Frank is online."
    mentions = [{
        "full_match": "@**Frank Liu (W1'19)**", 
        "name": "Frank Liu", 
        "pronouns": None
    }]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# Neopronouns
# -----------------------------
def test_neopronouns_ze_zir():
    content = "Gale is working. Ze completed the task."
    mentions = [{
        "full_match": "@**Gale Xy (ze/zir) (S2'15)**", 
        "name": "Gale Xy", 
        "pronouns": "ze/zir"
    }]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_neopronouns_xe_xem_no_pronouns_text():
    content = "Harper has no pronouns used nearby."
    mentions = [{
        "full_match": "@**Harper Q (xe/xem) (F2'20)**", 
        "name": "Harper Q", 
        "pronouns": "xe/xem"
    }]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_neopronouns_ey_em_wrong_pronouns():
    content = "Indi was writing. She wrote something."
    mentions = [{
        "full_match": "@**Indi Y (ey/em) (F1'25)**", 
        "name": "Indi Y", 
        "pronouns": "ey/em"
    }]

    results = parser.validate_mentions_in_text(content, mentions)
    assert not all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# Any pronouns
# -----------------------------
def test_any_pronouns_matches():
    content = "Jordan is typing. He responded quickly."
    mentions = [{
        "full_match": "@**Jordan Z (any) (W2'15)**", 
        "name": "Jordan Z", 
        "pronouns": "any"
    }]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


