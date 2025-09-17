###############################################################################
##  `bot.py`                                                                 ##
##                                                                           ##
##  Purpose: Handles all setup & logic for Zulip pronoun-proofer bot         ##
###############################################################################


from src.setup import create_client, subscribe_to_all_public_streams
from src.reader import scan_for_mentions
from src.logger import log_info, log_section_start, log_section_end, force_flush
    
from examples.real_world_test import run_real_world_test


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
    
    # For testing with real Zulip messages:
    # run_real_world_test(use_recent_message=False)


