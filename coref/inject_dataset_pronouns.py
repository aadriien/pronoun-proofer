import random
from collections import defaultdict
from datasets import load_dataset
from pathlib import Path

# Pronoun systems with consistent gender mappings
pronoun_systems = {
    'traditional_he': {
        'subjective': 'he',
        'objective': 'him', 
        'possessive': 'his',
        'reflexive': 'himself'
    },
    'traditional_she': {
        'subjective': 'she',
        'objective': 'her',
        'possessive': 'her', 
        'possessive_standalone': 'hers',
        'reflexive': 'herself'
    },
    'singular_they': {
        'subjective': 'they',
        'objective': 'them',
        'possessive': 'their',
        'possessive_standalone': 'theirs', 
        'reflexive': 'themselves'
    },
    'xe_xem': {
        'subjective': 'xe',
        'objective': 'xem',
        'possessive': 'xyr',
        'possessive_standalone': 'xyrs',
        'reflexive': 'xemself'
    },
    'ze_zir': {
        'subjective': 'ze',
        'objective': 'zem', 
        'possessive': 'zir',
        'possessive_standalone': 'zirs',
        'reflexive': 'zemself'
    },
    'ey_em': {
        'subjective': 'ey',
        'objective': 'em',
        'possessive': 'eir', 
        'possessive_standalone': 'eirs',
        'reflexive': 'emself'
    },
    'fae_faer': {
        'subjective': 'fae',
        'objective': 'faer',
        'possessive': 'faer',
        'possessive_standalone': 'faers', 
        'reflexive': 'faerself'
    }
}

# Pronoun mapping for replacement
pronoun_type_map = {
    'he': 'subjective',
    'she': 'subjective', 
    'him': 'objective',
    'her': 'objective',  # can also be possessive
    'his': 'possessive',
    'hers': 'possessive_standalone',
    'theirs': 'possessive_standalone',
    'himself': 'reflexive',
    'herself': 'reflexive',
    'themselves': 'reflexive'
}

# Load OntoNotes v5 English (v12) dataset from Hugging Face
print("Loading OntoNotes dataset...")
dataset = load_dataset("ontonotes/conll2012_ontonotesv5", "english_v12", trust_remote_code=True)

# Get label mappings  
sentences_features = dataset['train'].features['sentences'][0]  # Get the dict from the list
pos_labels = sentences_features['pos_tags'].feature.names
ner_labels = sentences_features['named_entities'].feature.names

print(f"Dataset loaded with {len(dataset['train'])} train, {len(dataset['validation'])} validation, {len(dataset['test'])} test documents")

def replace_pronoun_with_system(word, pronoun_system):
    """Replace a pronoun using the specified system."""
    word_lower = word.lower()
    
    if word_lower not in pronoun_type_map:
        return word
        
    pronoun_type = pronoun_type_map[word_lower]
    
    # Handle ambiguous 'her' - check if it's possessive or objective
    if word_lower == 'her':
        # For now, assume possessive if system has separate possessive form
        replacement = pronoun_system.get('possessive', word)
    else:
        replacement = pronoun_system.get(pronoun_type, word)
    
    # Preserve capitalization
    if word and word[0].isupper():
        replacement = replacement.capitalize()
        
    return replacement

def process_document(doc):
    """Process a single document, replacing pronouns consistently within coreference clusters."""
    doc_id = doc["document_id"].replace("/", "_")
    
    # Build coreference clusters - map cluster_id -> list of (sent_idx, word_idx)
    coref_clusters = defaultdict(list)
    pronoun_clusters = defaultdict(list)  # Only clusters containing pronouns
    
    for sent_idx, sentence in enumerate(doc["sentences"]):
        words = sentence["words"]
        
        # Process coref spans: [cluster_id, start_token, end_token]
        for cluster_id, start_pos, end_pos in sentence["coref_spans"]:
            for word_idx in range(start_pos, end_pos + 1):
                if word_idx < len(words):  # bounds check
                    word = words[word_idx]
                    coref_clusters[cluster_id].append((sent_idx, word_idx))
                    
                    # Check if this word is a pronoun we want to replace
                    if word.lower() in pronoun_type_map:
                        pronoun_clusters[cluster_id].append((sent_idx, word_idx))
    
    # Assign random pronoun systems to clusters that contain pronouns
    cluster_systems = {}
    for cluster_id in pronoun_clusters:
        # Randomly choose a pronoun system for this cluster
        system_name = random.choice(list(pronoun_systems.keys()))
        cluster_systems[cluster_id] = pronoun_systems[system_name]
    
    # Build replacement mapping
    replacements = {}
    for cluster_id, system in cluster_systems.items():
        if cluster_id in pronoun_clusters:
            for sent_idx, word_idx in pronoun_clusters[cluster_id]:
                replacements[(sent_idx, word_idx)] = system
    
    return doc_id, replacements

def format_coref_spans(coref_spans, word_idx):
    """Format coreference spans for a specific word position."""
    annotations = []
    
    for cluster_id, start_pos, end_pos in coref_spans:
        if start_pos == word_idx and end_pos == word_idx:
            # Single token span
            annotations.append(f"({cluster_id})")
        elif start_pos == word_idx:
            # Start of multi-token span
            annotations.append(f"({cluster_id}")
        elif end_pos == word_idx:
            # End of multi-token span
            annotations.append(f"{cluster_id})")
    
    return "|".join(annotations) if annotations else "-"

def save_as_conll(dataset_split, filepath):
    """Save dataset split to proper CoNLL format with pronoun replacements."""
    print(f"Processing {len(dataset_split)} documents for {filepath}...")
    
    with open(filepath, "w", encoding="utf-8") as f:
        
        for doc_idx, doc in enumerate(dataset_split):
            if doc_idx % 1000 == 0:
                print(f"  Processed {doc_idx} documents...")
                
            doc_id, replacements = process_document(doc)
            
            for sent_idx, sentence in enumerate(doc["sentences"]):
                part_id = sentence["part_id"]
                words = sentence["words"]
                pos_tags = sentence["pos_tags"]
                speaker = sentence["speaker"]
                named_entities = sentence["named_entities"]
                coref_spans = sentence["coref_spans"]
                
                # Start document header
                f.write(f"#begin document ({doc_id}); part {part_id:03d}\n")
                
                # Process each token in the sentence
                for word_idx, word in enumerate(words):
                    # Replace pronoun if needed
                    if (sent_idx, word_idx) in replacements:
                        word = replace_pronoun_with_system(word, replacements[(sent_idx, word_idx)])
                    
                    pos_tag = pos_labels[pos_tags[word_idx]]
                    ner_tag = ner_labels[named_entities[word_idx]]
                    coref_annotation = format_coref_spans(coref_spans, word_idx)
                    
                    # Write CoNLL line: doc_id part_id word_id word pos parse pred_lemma pred_frame word_sense speaker ner coref
                    f.write(f"{doc_id} {part_id} {word_idx} {word} {pos_tag} (*) - - - {speaker} {ner_tag} {coref_annotation}\n")
                
                f.write("\n")  # empty line between sentences
                f.write("#end document\n")
                
    print(f"Completed processing {filepath}")

# Directory to save CoNLL files
Path("conll_output").mkdir(exist_ok=True)

# Process each split
for split in ["train", "validation", "test"]:
    print(f"\nProcessing {split} split...")
    save_as_conll(dataset[split], f"conll_output/{split}.conll")

print("\nAll files generated successfully!")

