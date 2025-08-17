import random
from datasets import load_dataset


# Expanded mapping including he/she, singular they, xe/ze/ey, and fae/faer
pronoun_replacement_map = {
    "he":      ["he", "they", "xe", "ze", "ey", "fae"],
    "him":     ["him", "them", "xem", "zem", "em", "faer"],
    "his":     ["his", "their", "xyr", "zir", "eir", "faers"],
    "himself": ["himself", "themselves", "xemself", "zemself", "emself", "faerself"],
    
    "she":     ["she", "they", "xe", "ze", "ey", "fae"],
    "her":     ["her", "them", "xem", "zem", "em", "faer"],
    "hers":    ["hers", "theirs", "xyrs", "zirs", "eirs", "faers"],
    "herself": ["herself", "themselves", "xemself", "zemself", "emself", "faerself"]
}


# Load OntoNotes v5 English (v12) dataset from Hugging Face
dataset = load_dataset("ontonotes/conll2012_ontonotesv5", "english_v12")

def replace_pronouns(tokens):
    """Randomly replace singular pronouns in a list of tokens."""
    return [
        random.choice(pronoun_replacement_map[token.lower()])
        if token.lower() in pronoun_replacement_map
        else token
        for token in tokens
    ]

# Apply replacements across all splits
for split in ["train", "validation", "test"]:
    for doc in dataset[split]:
        for sentence in doc["sentences"]:
            sentence["words"] = replace_pronouns(sentence["words"])

# Optional: save the modified dataset for future use
dataset.save_to_disk("modified_ontonotes_v12")


