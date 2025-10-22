# ✍️📓 Pronoun Proofer

## Description

Meet the `Pronoun Proofer`, a Zulip bot that validates the usage of pronouns in a given text to ensure they match the preferences of the people being referenced. This bot now leverages NLP for clever parsing!

This constructive tool is designed to improve the community experience at RC by helping people identify and fix any mistaken pronouns. `Pronoun Proofer` will NOT punish, shame, or embarrass people when they slip up. 

Instead, it will reach out to them privately so that they are aware of the potential mismatch, encouraging them to review and edit their message to reflect the correct pronouns. With the help of this bot, folks in the community can connect with one another on a deeper and more respectful level! 


## How It Works

### *`Pronoun Proofer` runs 24/7 on [RC's Heap Community Cluster](https://www.recurse.com/blog/126-heap-sponsors-rc-community-cluster)*

>#### Listening
>1. Zulip bot is subscribed to all public streams
>2. New message event in a stream triggers validation pipeline
>3. Alternatively, pipeline triggered by update message (edit) event 

>#### Scanning
>4. Bot scans for any mentions (@) in message content
>5. Name + pronouns are extracted from Zulip name tag markdown

>#### Parsing
>6. NLP is applied to full text content, generating clusters for entities
>7. All mentioned names are linked to their cluster pronouns
>8. Mappings are reviewed to check for any discrepancies

>#### Resolving
>9. Any detected mismatches are flagged for notification service
>10. Bot privately DMs writer of message, with a link to revisit + edit


## Tools / Tech

- **Python**: logic with Zulip client
- **spaCy (NLP)**: experimental coreference pipeline
    - cluster component
    - span resolver component
- **OpenAI (LLM)**: secondary text check (currently disabled)
- **Linux**: Bash scripts for RC's heap cluster
    - user instance of `systemd`
    - `.service` files run with `enable-linger`
    - `.timer` file to act as cron job for log extraction


## Getting Started

Python dependencies are managed by Poetry.

To **install** dependencies:
```
make setup
```

For a **fast run**:
```
make all
```

### For the Zulip bot:

To run bot in **production** (listen for and respond to messages 24/7):
```
make run-prod
```

To run bot in **development** (one-off real-world testing instance):
```
make run-dev
```

To run a series of **unit tests** for the bot:
```
make tests
```

### For the coreference model (NLP):

To iteratively **fine-tune** model:
```
make fine_tune_model
```


## Acknowledgements

### People

A massive thank you to the wonderful community of builders, creators, and programmers at [the Recurse Center](https://www.recurse.com)! 

And speaking of people at RC.. I'd especially like to thank [Florian Ragwitz](https://github.com/rafl), who paired with me on this project! Florian's Linux expertise is what helped get `Pronoun Proofer` onto the heap cluster, and the two of us also collaborated on property-based testing. 

The feedback and edge cases provided by folks at RC have really helped this bot grow and evolve with time. Stay tuned as I continue to iterate on training / fine-tuning for improved NLP! 


