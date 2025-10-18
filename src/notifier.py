###############################################################################
##  `notifier.py`                                                            ##
##                                                                           ##
##  Purpose: Alerts creator of message in event of pronoun error             ##
###############################################################################


import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

from src.logger import log_info, log_section_start, log_divider


BOT_CREATOR_TAG = "@**Adrien Lynch (he/they) (S2'25)**"

SPACY_OVERVIEW_URL = "https://explosion.ai/blog/coref"
SPACY_LINK_MARKDOWN = f"[coreference model]({SPACY_OVERVIEW_URL})"

GITHUB_REPO_URL = "https://github.com/aadriien/pronoun-proofer"
GITHUB_LINK_MARKDOWN = f"[work in progress]({GITHUB_REPO_URL})"

testing_bot_disclaimer = [
    f"\n—\n"
    f"**Note from the creator:** This bot is using spaCy's experimental " 
    f"{SPACY_LINK_MARKDOWN} (NLP) to detect pronoun references in a given "
    f"text and generate corresponding clusters. "
    f"It's still a {GITHUB_LINK_MARKDOWN}, so please reach out to "
    f"{BOT_CREATOR_TAG} if you notice any bugs or have questions!"
]


load_dotenv()

def get_message_link(content):
    zulip_domain = os.getenv("ZULIP_SITE")

    if not zulip_domain:
        raise ValueError("ZULIP_SITE must be set in .env")
    
    if content.get("message_type") == "stream":
        stream_id = content.get("stream_id")
        topic = content.get("subject")
        message_id = content.get("id")

        if stream_id and topic and message_id:
            topic_encoded = quote_plus(topic)
            return f"{zulip_domain}/#narrow/stream/{stream_id}/topic/{topic_encoded}/near/{message_id}"
    return None


def notify_writer_of_mismatch(content, result, client):
    sender_id = content["sender_id"]
    # sender_email = content["sender_email"]
    sender_full_name = content["sender_full_name"]
    sender_name = sender_full_name.split()[0]

    mentioned_name, mentioned_pronouns = result["name"], result["pronouns"]

    if result["mismatches"]:
        quoted_mismatches = [f'\"{mismatch}\"' for mismatch in result["mismatches"]]
        mismatches_str = ", ".join(quoted_mismatches) 

    content_lines = [
        f"Hi {sender_name.strip()}! I noticed your recent message may have used pronouns "
        f"that don't match {mentioned_name}'s preferences ({mentioned_pronouns}). "
        f"NLP detected the following mismatches: {mismatches_str}"
    ]

    # Add link if message is from a stream
    zulip_message_link = get_message_link(content)
    content_lines.append(f"You can review your original message here: {zulip_message_link}")

    # Log main DM content that will be sent to writer (without info overview)
    log_section_start("SENDING DM NOTIFICATION")
    log_info(f"Recipient: {sender_full_name} (ID: {sender_id})")
    log_divider()
    log_info(f"Main DM Content: {' '.join(content_lines)}")

    content_lines.extend(testing_bot_disclaimer)

    client.send_message({
        "type": "private",
        "to": [sender_id],
        "content": "\n\n".join(content_lines)
    })



