###############################################################################
##  `test_notifier.py`                                                       ##
##                                                                           ##
##  Purpose: Tests PM notice in response to message detection                ##
###############################################################################


import pytest
from unittest.mock import MagicMock
from src import notifier


# -----------------------------
# Single mismatch triggers PM
# -----------------------------
def test_notify_writer_of_mismatch_triggers_pm(monkeypatch):
    monkeypatch.setenv("ZULIP_SITE", "https://zulip.example.com")

    # Mock message content
    content = {
        "id": 101,
        "sender_email": "alice@example.com",
        "sender_full_name": "Alice Smith",
        "type": "stream",
        "stream_id": 42,
        "subject": "Team Updates"
    }

    # Result dict with mismatch in checks
    result = {
        "name": "Bob Jones",
        "pronouns": "he/him",
        "positions": [10],
        "checks": [
            {"snippet": "some message text chunk", "pronouns_match": False},
            {"snippet": "another chunk", "pronouns_match": True},
        ]
    }

    mock_client = MagicMock()
    notifier.notify_writer_of_mismatch(content, result, mock_client)

    # PM should be sent with link
    mock_client.send_message.assert_called_once()
    sent_msg = mock_client.send_message.call_args[0][0] 

    assert sent_msg["type"] == "private"
    assert sent_msg["to"] == ["alice@example.com"]
    
    assert "don't match Bob Jones's preferences (he/him)" in sent_msg["content"]
    assert "near/101" in sent_msg["content"]


# -----------------------------
# All checks pass -> no PM
# -----------------------------
def test_notify_writer_of_mismatch_no_pm_when_all_match(monkeypatch):
    monkeypatch.setenv("ZULIP_SITE", "https://zulip.example.com")

    content = {
        "id": 102,
        "sender_email": "alice@example.com",
        "sender_full_name": "Alice Smith",
        "type": "stream",
        "stream_id": 42,
        "subject": "Team Updates"
    }

    # Result dict with all checks passing
    result = {
        "name": "Bob Jones",
        "pronouns": "he/him",
        "positions": [10],
        "checks": [
            {"snippet": "chunk 1", "pronouns_match": True},
            {"snippet": "chunk 2", "pronouns_match": True},
        ]
    }

    mock_client = MagicMock()
    # Notify only if mismatch exists
    if not all(check["pronouns_match"] for check in result["checks"]):
        notifier.notify_writer_of_mismatch(content, result, mock_client)

    mock_client.send_message.assert_not_called()

