###############################################################################
##  `bot.py`                                                                 ##
##                                                                           ##
##  Purpose: Handles all setup & logic for Zulip pronoun-proofer bot         ##
###############################################################################


from src.setup import create_client


class PronounBot:
    def __init__(self):
        self.client = create_client()



if __name__ == "__main__":
    bot = PronounBot()

