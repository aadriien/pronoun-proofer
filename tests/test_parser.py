###############################################################################
##  `test_parser.py`                                                         ##
##                                                                           ##
##  Purpose: Tests validation of name & pronouns in text                     ##
###############################################################################


import pytest
from src import parser
from src import mentions

# -----------------------------
# Single pronouns
# -----------------------------
def test_single_pronoun_she_nearby():
    content = "Alice is coding. She is doing well."
    nametags = mentions.get_mentions(
        "@**Alice Smith (she/her) (SP1'25)** "
    )

    results = parser.validate_mentions_in_text(content, nametags)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_single_pronoun_he_nearby():
    content = "Bob finished the task. He did it quickly."
    nametags = mentions.get_mentions(
        "@**Bob Jones (he/him) (F2'24)** "
    )

    results = parser.validate_mentions_in_text(content, nametags)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_single_pronoun_they_not_nearby():
    content = "Charlie said she is busy."
    nametags = mentions.get_mentions(
        "@**Charlie (they/them) (Faculty)** "
    )

    results = parser.validate_mentions_in_text(content, nametags)
    assert not all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# Multiple pronouns
# -----------------------------
def test_multiple_pronouns_match():
    content = "Dana shared her notes. Elliot did his part."
    nametags = mentions.get_mentions(
        "@**Dana Lee (she/they) (F1'24)** "
        "@**Elliot Kim (he/they) (F2'25)** "
    )

    results = parser.validate_mentions_in_text(content, nametags)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_multiple_pronouns_partial_match():
    content = "Dana used they pronouns. Elliot prefers he/him."
    nametags = mentions.get_mentions(
        "@**Dana Lee (she/they) (F1'24)** "
        "@**Elliot Kim (he/they) (F2'25)** "
    )

    results = parser.validate_mentions_in_text(content, nametags)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# No pronouns
# -----------------------------
def test_no_pronouns_in_tag():
    content = "Frank is online."
    nametags = mentions.get_mentions(
        "@**Frank Liu (W1'19)** "
    )

    results = parser.validate_mentions_in_text(content, nametags)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# Neopronouns
# -----------------------------
def test_neopronouns_ze_zir():
    content = "Gale is working. Ze completed the task."
    nametags = mentions.get_mentions(
        "@**Gale Xy (ze/zir) (S2'15)** "
    )

    results = parser.validate_mentions_in_text(content, nametags)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_neopronouns_xe_xem_no_pronouns_text():
    content = "Harper has no pronouns used nearby."
    nametags = mentions.get_mentions(
        "@**Harper Q (xe/xem) (F2'20)** "
    )

    results = parser.validate_mentions_in_text(content, nametags)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


def test_neopronouns_ey_em_wrong_pronouns():
    content = "Indi was writing. She wrote something."
    nametags = mentions.get_mentions(
        "@**Indi Y (ey/em) (F1'25)** "
    )

    results = parser.validate_mentions_in_text(content, nametags)
    assert not all(check["pronouns_match"] for r in results for check in r["checks"])


# -----------------------------
# Any pronouns
# -----------------------------
def test_any_pronouns_matches():
    content = "Jordan is typing. He responded quickly."
    nametags = mentions.get_mentions(
        "@**Jordan Z (any) (W2'15)** "
    )

    results = parser.validate_mentions_in_text(content, nametags)
    assert all(check["pronouns_match"] for r in results for check in r["checks"])


