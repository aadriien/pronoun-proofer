###############################################################################
##  `bot.py`                                                                 ##
##                                                                           ##
##  Purpose: Handles all setup & logic for Zulip pronoun-proofer bot         ##
###############################################################################


import warnings
warnings.filterwarnings("ignore")

import click # for args via CLI 

from src.setup import create_client
from src.utils import subscribe_to_all_public_streams
from src.reader import scan_for_mentions
from src.logger import log_info, log_section_start, log_section_end, log_blank_line, force_flush
    
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
        log_blank_line()
        force_flush()

    def run(self):
        log_info("Starting message monitoring...")
        log_info("Bot is now listening for messages with mentions (@)")
        force_flush()
        
        self.client.call_on_each_event(
            lambda event: scan_for_mentions(self.event_to_msg(event), self.client), 
            event_types=["message", "update_message"]
        )


    def event_to_msg(self, event):
        if not event["type"] in ["message", "update_message"]:
            raise ValueError("ERROR: Invalid event type")
        
        match event["type"]:

            # Construct message object from new `message` event
            case "message":
                msg_obj = event["message"]

                return {
                    "event_type": event.get("type", ""),
                    "message_type": msg_obj.get("type", ""), # `type` == `stream`

                    "stream_id": msg_obj.get("stream_id", ""),
                    "subject": msg_obj.get("subject", ""),
                    "id": msg_obj.get("id", ""),

                    "sender_id": msg_obj.get("sender_id", ""),

                    "sender_email": msg_obj.get("sender_email", ""),
                    "sender_full_name": msg_obj.get("sender_full_name", ""),

                    "content": msg_obj.get("content", ""),
                }
            
            # Construct message object from `message_update` event (edited existing message)
            case "update_message":
                original_msg = self.client.get_raw_message(event["message_id"])
                msg_obj = original_msg["message"]

                return {
                    "event_type": event.get("type", ""),
                    "message_type": msg_obj.get("type", ""), # `type` == `stream`

                    "stream_id": msg_obj.get("stream_id", ""),
                    "subject": msg_obj.get("subject", ""),
                    "id": event.get("message_id", ""),

                    "sender_id": event.get("user_id", ""),

                    "sender_email": msg_obj.get("sender_email", ""),
                    "sender_full_name": msg_obj.get("sender_full_name", ""),

                    "content": event.get("content", ""),
                }


# Instantiate bot just once as a global so Click can access it 
bot = PronounBot()


@click.command()
@click.option("--prod", is_flag=True, help="Run in service mode (24/7 live bot)")
@click.option("--dev", is_flag=True, help="Run in dev mode (one-off test)")
def launch_program(prod, dev):
    # Ensure only 1 mode specified
    flags = [prod, dev]
    if sum(flags) != 1:
        raise click.UsageError("ERROR: You must provide exactly one of --prod or --dev")

    # Bot acts as a live service running 24/7 to listen for messages
    if prod:
        click.echo("Running in prod (service) mode...")
        bot.run()

    # Bot acts as a one-off script (real world Zulip message example) to test locally
    elif dev:
        click.echo(f"Running in dev (test) mode...")
        run_real_world_test(use_recent_message=False)

    else:
        raise click.UsageError("ERROR: Please specify --prod or --dev")


if __name__ == "__main__":
    # Python Click to pass CLI arguments
    # For example,
    #   `python3 bot.py --prod`
    #   `python3 bot.py --dev`
    # Or alternativey, with Makefile rules
    #   `make run-prod`
    #   `make run-dev`

    launch_program()

