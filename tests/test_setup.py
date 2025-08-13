###############################################################################
##  `test_setup.py`                                                          ##
##                                                                           ##
##  Purpose: Tests creation of Zulip client instance for bot                 ##
###############################################################################


import pytest
from src.setup import create_client


def test_create_client():
    client = create_client()
    assert client is not None 

    from zulip import Client
    assert isinstance(client, Client)

