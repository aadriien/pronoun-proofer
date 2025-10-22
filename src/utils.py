###############################################################################
##  `utils.py`                                                               ##
##                                                                           ##
##  Purpose: Handles Zulip functionality for processing message streams      ##
###############################################################################


from src.logger import log_info


def subscribe_to_all_public_streams(client):
    # Get all streams bot can see
    streams_response = client.get_streams()
    if streams_response["result"] != "success":
        raise RuntimeError(f"Failed to fetch streams: {streams_response}")

    # Get streams bot is already subscribed to
    subs_response = client.get_subscriptions()
    if subs_response["result"] != "success":
        raise RuntimeError(f"Failed to fetch subscriptions: {subs_response}")

    current_subs = {s["name"] for s in subs_response["subscriptions"]}

    # Only include streams bot isn't already subscribed to
    streams_to_subscribe = [
        {"name": stream["name"]}
        for stream in streams_response["streams"]
        if stream["name"] not in current_subs
    ]

    if streams_to_subscribe:
        add_resp = client.add_subscriptions(streams_to_subscribe)
        if add_resp["result"] != "success":
            raise RuntimeError(f"Failed to subscribe: {add_resp}")
        return [s["name"] for s in streams_to_subscribe]

    return []


def fetch_latest_messages(client, channel_stream_id, topic_subject_id, count = 5):
    # Fetch list of most recent messages from specified channel / topic
    result = client.get_messages({
        "anchor": "newest",
        "num_before": count,
        "num_after": 0,
        "narrow": [
            {"operator": "channel", "operand": channel_stream_id},
            {"operator": "topic", "operand": topic_subject_id},
        ],
        "apply_markdown": False
    })

    log_info("Recent message fetch result:")
    log_info(f"Found {len(result.get('messages', []))} message(s)")

    # Stored as array of message objects
    return result.get("messages", [])


def fetch_last_message(client, channel_stream_id, topic_subject_id):
    # Leverage helper function with constraint of 1 message
    latest_arr = fetch_latest_messages(
        client, 
        channel_stream_id, topic_subject_id, 
        count=1
    )

    if latest_arr:
        # Get 0th message object
        last_msj_obj = latest_arr[0]
        return last_msj_obj

    return None



