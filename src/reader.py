###############################################################################
##  `reader.py`                                                              ##
##                                                                           ##
##  Purpose: Fetches new message events in real time                         ##
###############################################################################


from src.mentions import get_mentions
from src.parser import validate_mentions_in_text
from src.notifier import notify_writer_of_mismatch
from src.logger import (
    log_info, log_debug,
    log_section_start, log_section_end, 
    log_mention_info, 
    log_validation_results, 
    force_flush
)


REQUIRED_FIELDS = [
    "event_type",
    "message_type",
    "stream_id",
    "subject",
    "id",
    "sender_id",
    "sender_email",
    "sender_full_name",
    "content"
]

def contents_are_valid(message):
    if not all(field in message for field in REQUIRED_FIELDS):
        log_debug("Fields missing from message, exiting...")
        return False
    
    for val in message.values():
        if val == "":
            log_debug("Fields empty in message, exiting...")
            return False

    return True 


def scan_for_mentions(message, client):
    # Confirm all required fields available
    # e.g. prevent Pronoun Proofer from checking its own messages
    if not contents_are_valid(message):
        return
    
    content = message["content"]
    
    log_section_start("MESSAGE SCAN")
    
    if "@" in content:
        mentions = get_mentions(content)
        
        if mentions:
            log_info(f"Found {len(mentions)} mention(s) to process")
            for mention in mentions:
                log_mention_info(mention)
            
            results = validate_mentions_in_text(content, mentions)
            log_validation_results(results, "Final Validation")
            
            # Check for mismatches & notify
            mismatches = [r for r in results if not r['pronouns_match']]
            if mismatches:
                log_info(f"Found {len(mismatches)} pronoun mismatch(es) - sending notifications")
                for r in mismatches:
                    notify_writer_of_mismatch(message, r, client)
                    pass
            else:
                log_info("All pronoun usage is correct!")
        else:
            log_info("No valid mentions found in message")
    else:
        log_info("No mentions (@) found in message")
    
    log_section_end("MESSAGE SCAN")
    force_flush()

