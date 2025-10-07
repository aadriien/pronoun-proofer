###############################################################################
##  `model_utils.py`                                                         ##
##                                                                           ##
##  Purpose: Load & prep raw data as well as resulting model versions        ##
###############################################################################


import warnings
warnings.filterwarnings("ignore")

import os
import json
import spacy

from spacy.training import Example
from datetime import datetime


BASE_MODEL = "en_coreference_web_trf"
NEW_MODELS_PREFIX = "coref_"

NEW_MODELS_FOLDER = "models"
TRAINING_DATA_FOLDER = "training-data"

THEY_THEM_DATA = "they-them.json"


def load_training_data(json_file = THEY_THEM_DATA):
    # Load training examples from JSON file
    filepath = os.path.join(os.path.dirname(__file__), TRAINING_DATA_FOLDER, json_file)
    with open(filepath, "r") as f:
        return json.load(f)


def create_training_examples(nlp, training_data):
    # Convert JSON data to spaCy training examples
    examples = []
    debug_count = 0
    
    for item in training_data:
        text = item["text"]
        clusters = item["clusters"]
        
        # Create doc
        doc = nlp.make_doc(text)
        
        # Create span annotations for coreference
        spans = {}
        for i, cluster in enumerate(clusters):
            span_positions = []
            
            # Find token positions for each mention in cluster
            for mention in cluster:
                mention_lower = mention.lower().strip()
                found = False
                
                # Try exact token matching first
                for j, token in enumerate(doc):
                    if token.lower_ == mention_lower:
                        span_positions.append((j, j + 1))

                        # Only find first occurrence to avoid duplicates
                        found = True
                        break 
                
                # Try multi-token matching for phrases if not found
                if not found:
                    for start_idx in range(len(doc)):

                        for end_idx in range(start_idx + 1, min(start_idx + 4, len(doc) + 1)):
                            span_text = ' '.join([t.lower_ for t in doc[start_idx:end_idx]])
                            
                            if span_text == mention_lower:
                                span_positions.append((start_idx, end_idx))
                                found = True
                                break

                        if found:
                            break
            
            if span_positions:
                spans[f"coref_clusters_{i+1}"] = span_positions
        
        # Only add examples that have spans
        if spans:
            annotations = {"spans": spans}
            example = Example.from_dict(doc, annotations)
            examples.append(example)
            
            # Debug first few examples
            if debug_count < 3:
                print(f"  Debug example {debug_count + 1}: '{text}'")
                print(f"    Clusters: {clusters}")
                print(f"    Spans: {spans}")
                debug_count += 1
        else:
            # Debug why no spans were found
            if debug_count < 3:
                print(f"  No spans found for: '{text}'")
                print(f"    Tokens: {[t.text for t in doc]}")
                print(f"    Clusters: {clusters}")
    
    return examples


def load_base_model():
    # Load base coreference model (spaCy experimental default)
    print(f"Loading base model: {BASE_MODEL}")
    try:
        nlp = spacy.load(BASE_MODEL)
        print(f"Successfully loaded {BASE_MODEL}")
        return nlp
    except OSError as e:
        print(f"Error loading model: {e}")
        return None


def get_latest_model():
    # Find latest fine-tuned model to continue training from
    models_dir = os.path.join(os.path.dirname(__file__), NEW_MODELS_FOLDER)
    if not os.path.exists(models_dir):
        return None
    
    model_dirs = [d for d in os.listdir(models_dir) 
                  if os.path.isdir(os.path.join(models_dir, d)) 
                  and d.startswith(NEW_MODELS_PREFIX)]
    
    if not model_dirs:
        return None
    
    # Sort by timestamp in filename
    latest_model = sorted(model_dirs)[-1]
    model_path = os.path.join(models_dir, latest_model)
    
    try:
        nlp = spacy.load(model_path)
        print(f"Continuing from latest model: {latest_model}")
        return nlp
    except:
        print(f"Failed to load {latest_model}, starting from base model")
        return load_base_model()


def save_model_version(nlp):
    # Save model to versioned directory
    models_dir = os.path.join(os.path.dirname(__file__), NEW_MODELS_FOLDER)
    os.makedirs(models_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_name = f"{NEW_MODELS_PREFIX}{timestamp}"
    model_path = os.path.join(models_dir, version_name)

    nlp.to_disk(model_path)
    print(f"Model version saved to: {model_path}")
    return model_path
    

    
