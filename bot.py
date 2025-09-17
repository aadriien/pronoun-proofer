###############################################################################
##  `bot.py`                                                                 ##
##                                                                           ##
##  Purpose: Handles all setup & logic for Zulip pronoun-proofer bot         ##
###############################################################################


from src.setup import create_client, subscribe_to_all_public_streams
from src.reader import scan_for_mentions
from src.logger import log_info, log_section_start, log_section_end, force_flush


class PronounBot:
    def __init__(self):
        log_section_start("PRONOUN BOT INITIALIZATION")
        log_info("Creating Zulip client...")
        self.client = create_client()
        log_info("Subscribing to public streams...")
        self.subscribed_streams = subscribe_to_all_public_streams(self.client)
        log_info(f"Subscribed to {len(self.subscribed_streams)} streams")
        log_section_end("PRONOUN BOT INITIALIZATION")
        force_flush()

    def run(self):
        log_info("Starting message monitoring...")
        log_info("Bot is now listening for messages with mentions (@)")
        force_flush()
        self.client.call_on_each_message(
            lambda msg: scan_for_mentions(msg, self.client)
        )


if __name__ == "__main__":
    bot = PronounBot()
    bot.run()



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

    log_info("Test message fetch result:")
    log_info(f"Found {len(result.get('messages', []))} message(s)")
    message = result["messages"][0]
    # print(message["content"])
    # print("\n")

    # message["content"] += " testing with @**Adrien Lynch (he/they) (S2'25)**"
    # message["content"] += " testing she pronouns for Adrien to see her outcome"

    # message["content"] += " now testing with @**Test Person (she/ze) (W1'17)**"
    # message["content"] += " now testing he pronouns for Test to see their outcome"


    message["content"] += (
        "\n\n"
        "I met with with @**Adrien Lynch (he/they) (S2'25)** today. "
        "They showed me what they were working on. "
        "Adrien's work is really cool. I love seeing his projects. "
        "I also worked with @**Test Person (she/ze) (W1'17)**. "
        "Test has so many cool ideas in his mind. Ze are the best."
    )

    log_section_start("TEST MESSAGE PROCESSING")
    log_info("Processing test message...")

    scan_for_mentions(message, bot.client)


