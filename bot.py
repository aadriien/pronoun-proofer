###############################################################################
##  `bot.py`                                                                 ##
##                                                                           ##
##  Purpose: Handles all setup & logic for Zulip pronoun-proofer bot         ##
###############################################################################


from src.setup import create_client, subscribe_to_all_public_streams
from src.reader import scan_for_mentions


class PronounBot:
    def __init__(self):
        self.client = create_client()
        self.subscribed_streams = subscribe_to_all_public_streams(self.client)

    def run(self):
        self.client.call_on_each_message(scan_for_mentions)


if __name__ == "__main__":
    bot = PronounBot()


    result = bot.client.get_messages({
        "anchor": "newest",        # get the newest message
        "num_before": 1,           # how many messages before the anchor
        "num_after": 0,            # how many messages after
        "narrow": [
            ["channel", "checkins"],
            ["topic", "Adrien Lynch"]
        ],
        "apply_markdown": False    # keep raw Markdown
    })

    print(result)
    print("\n\n")
    message = result["messages"][0]
    print(message["content"])

    scan_for_mentions(message["content"])

