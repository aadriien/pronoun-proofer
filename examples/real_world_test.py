###############################################################################
##  `real_world_test.py`                                                    ##
##                                                                           ##
##  Purpose: Real-world testing with actual Zulip messages                  ##
###############################################################################


from src.setup import create_client
from src.reader import scan_for_mentions
from src.logger import log_info, log_section_start, log_section_end


def create_test_message_content():
    # Test message content with known pronoun patterns
    return (
        "I met with @**Adrien Lynch (he/they) (S2'25)** today. "
        "They showed me what they were working on. "
        "Adrien's work is really cool. I love seeing his projects. "
        "I also worked with @**Test Person (she/ze) (W1'17)**. "
        "Test has so many cool ideas in his mind. Ze are the best."
    )


def fetch_recent_message(client, channel="checkins", topic="Adrien Lynch"):
    # Fetch most recent message from specified channel / topic
    result = client.get_messages({
        "anchor": "newest",
        "num_before": 1,
        "num_after": 0,
        "narrow": [
            ["channel", channel],
            ["topic", topic]
        ],
        "apply_markdown": False
    })
    
    log_info("Recent message fetch result:")
    log_info(f"Found {len(result.get('messages', []))} message(s)")
    
    if result.get("messages"):
        return result["messages"][0]
    return None


def run_real_world_test(use_recent_message=False, channel="checkins", topic="Adrien Lynch"):
    # Run real-world testing with Zulip client
    log_section_start("REAL WORLD TEST")
    
    log_info("Creating Zulip client...")
    client = create_client()
    
    if use_recent_message:
        # Test with actual recent message
        message = fetch_recent_message(client, channel, topic)
        if not message:
            log_info("No recent message found, falling back to test content")
            message = {"content": create_test_message_content()}
    else:
        # Test with predefined content
        message = {"content": create_test_message_content()}
    
    # Append additional test content if desired
    # message["content"] += "\n\nAdditional test scenarios can be added here"
    
    log_info("Processing test message...")
    scan_for_mentions(message, client)
    
    log_section_end("REAL WORLD TEST")


if __name__ == "__main__":
    # Run test when script is executed directly
    run_real_world_test(use_recent_message=False)
    
