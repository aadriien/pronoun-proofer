# ✍️📓 Pronoun Proofer

## Description

Meet the `Pronoun Proofer`, a Zulip bot that validates the usage of pronouns in a given text to ensure they match the preferences of the people being referenced. This bot now leverages NLP for clever parsing!

This constructive tool is designed to improve the community experience at RC by helping people identify and fix any mistaken pronouns. `Pronoun Proofer` will NOT punish, shame, or embarrass people when they slip up. Instead, it will reach out to them privately so that they are aware of the potential mismatch, encouraging them to review and edit their message to reflect the correct pronouns. With the help of this bot, folks in the community can connect with one another on a deeper and more respectful level! 


## How It Works

1. Zulip bot is subscribed to all public streams
2. New message event in a stream triggers validation pipeline
3. Bot scans for any mentions (@) in message content
4. Name + pronouns are extracted from Zulip name tag markdown
5. NLP is applied to full text content, generating clusters for entities
6. All mentioned names are linked to their cluster pronouns
7. Mappings are reviewed to check for any discrepancies
8. Any detected mismatches are flagged for notification service
9. Bot privately DMs writer of message, with a link to revisit + edit


## Tools / Tech

- **Python**: scripts with Zulip client
- **spaCy (NLP)**: experimental coreference pipeline
    - cluster component
    - span resolver component


## Acknowledgements

### People

A massive thank you to the wonderful community of builders, creators, and programmers at [the Recurse Center](https://www.recurse.com)! 

The feedback and edge cases provided by folks at RC have really helped this bot grow and evolve with time. Stay tuned as I continue to iterate on training / fine-tuning for improved NLP! 


