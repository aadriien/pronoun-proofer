###############################################################################
##  `setup.py`                                                               ##
##                                                                           ##
##  Purpose: Creates a Zulip client instance for bot to operate              ##
###############################################################################


import os
import zulip
from dotenv import load_dotenv


load_dotenv()

def create_client():
    email = os.getenv("ZULIP_BOT_EMAIL")
    api_key = os.getenv("ZULIP_API_KEY")

    if not email or not api_key:
        raise ValueError("ZULIP_BOT_EMAIL and ZULIP_API_KEY must be set in .env")

    return zulip.Client(email=email, api_key=api_key)


def subscribe_to_all_public_streams(client):
    # Get all streams bot can see 
    streams_response = client.get_streams()

    if streams_response["result"] != "success":
        raise RuntimeError(f"Failed to fetch streams: {streams_response}")

    streams = streams_response["streams"]
    streams_to_subscribe = [
        {"name": stream["name"]}
        for stream in streams
    ]

    if streams_to_subscribe:
        client.add_subscriptions(streams_to_subscribe)


