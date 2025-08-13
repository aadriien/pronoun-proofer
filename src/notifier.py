###############################################################################
##  `notifier.py`                                                            ##
##                                                                           ##
##  Purpose: Alerts creator of message in event of pronoun error             ##
###############################################################################


import os
from dotenv import load_dotenv
from urllib.parse import quote_plus


load_dotenv()

def get_message_link(content):
    zulip_domain = os.getenv("ZULIP_SITE")

    if not zulip_domain:
        raise ValueError("ZULIP_SITE must be set in .env")
    
    if content.get("type") == "stream":
        stream_id = content.get("stream_id")
        topic = content.get("subject")
        message_id = content.get("id")

        if stream_id and topic and message_id:
            topic_encoded = quote_plus(topic)
            return f"{zulip_domain}/#narrow/stream/{stream_id}/topic/{topic_encoded}/near/{message_id}"
    return None


def notify_writer_of_mismatch(content, result, client):
    sender_email = content["sender_email"]
    sender_name = content["sender_full_name"].split()[0]

    mentioned_name, mentioned_pronouns = result["name"], result["pronouns"]

    content_lines = [
        f"Hi {sender_name.strip()}! I noticed your recent message may have used pronouns "
        f"that don't match {mentioned_name}'s preferences ({mentioned_pronouns})."
    ]

    # Add link if message is from a stream
    zulip_message_link = get_message_link(content)
    content_lines.append(f"You can review your original message here: {zulip_message_link}")

    client.send_message({
        "type": "private",
        "to": [sender_email],
        "content": "\n\n".join(content_lines)
    })



