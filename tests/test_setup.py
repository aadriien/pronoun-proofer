###############################################################################
##  `test_setup.py`                                                          ##
##                                                                           ##
##  Purpose: Tests creation of Zulip client instance for bot                 ##
###############################################################################


import pytest
from unittest.mock import MagicMock
from src.setup import create_client, subscribe_to_all_public_streams


def test_create_client():
    client = create_client()
    assert client is not None 

    from zulip import Client
    assert isinstance(client, Client)


def test_subscribe_to_all_public_streams():
    mock_client = MagicMock()

    # Simulate get_streams response with some unsubscribed streams
    mock_client.get_streams.return_value = {
        "result": "success",
        "streams": [
            {"name": "general", "subscribed": True},
            {"name": "random", "subscribed": False},
            {"name": "social", "subscribed": False},
        ]
    }

    # Simulate current subscriptions 
    mock_client.get_subscriptions.return_value = {
        "result": "success",
        "subscriptions": [
            {"name": "general"}
        ]
    }

    # Simulate successful subscription call
    mock_client.add_subscriptions.return_value = {"result": "success"}
    subscribe_to_all_public_streams(mock_client)

    # Should attempt to subscribe only to unsubscribed streams
    mock_client.add_subscriptions.assert_called_once_with([
        {"name": "random"},
        {"name": "social"}
    ])

