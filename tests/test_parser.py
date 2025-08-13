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
    mentions = [{"name": "Alice Smith", "pronouns": "she/her"}]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_single_pronoun_he_nearby():
    content = "Bob finished the task. He did it quickly."
    mentions = [{"name": "Bob Jones", "pronouns": "he/him"}]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_single_pronoun_they_not_nearby():
    content = "Charlie said she is busy."
    mentions = [{"name": "Charlie", "pronouns": "they/them"}]

    results = parser.validate_mentions_in_text(content, mentions)
    assert not all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# Multiple pronouns
# -----------------------------
def test_multiple_pronouns_match():
    content = "Dana shared her notes. Elliot did his part."
    mentions = [
        {"name": "Dana Lee", "pronouns": "she/they"},
        {"name": "Elliot Kim", "pronouns": "he/they"}
    ]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_multiple_pronouns_partial_match():
    content = "Dana used they pronouns. Elliot prefers he/him."
    mentions = [
        {"name": "Dana Lee", "pronouns": "she/they"},
        {"name": "Elliot Kim", "pronouns": "he/they"}
    ]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# No pronouns
# -----------------------------
def test_no_pronouns_in_tag():
    content = "Frank is online."
    mentions = [{"name": "Frank Liu", "pronouns": None}]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# Neopronouns
# -----------------------------
def test_neopronouns_ze_zir():
    content = "Gale is working. Ze completed the task."
    mentions = [{"name": "Gale Xy", "pronouns": "ze/zir"}]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_neopronouns_xe_xem_no_pronouns_text():
    content = "Harper has no pronouns used nearby."
    mentions = [{"name": "Harper Q", "pronouns": "xe/xem"}]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_neopronouns_ey_em_wrong_pronouns():
    content = "Indi was writing. She wrote something."
    mentions = [{"name": "Indi Y", "pronouns": "ey/em"}]

    results = parser.validate_mentions_in_text(content, mentions)
    assert not all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# Any pronouns
# -----------------------------
def test_any_pronouns_matches():
    content = "Jordan is typing. He responded quickly."
    mentions = [{"name": "Jordan Z", "pronouns": "any"}]

    results = parser.validate_mentions_in_text(content, mentions)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])
