###############################################################################
##  `fine_tune_model.py`                                                     ##
##                                                                           ##
##  Purpose: Incrementally fine-tune spaCy coreference model                 ##
###############################################################################


import warnings
warnings.filterwarnings("ignore")

import spacy
from spacy.training import Example
import json
import random
from datetime import datetime
import os


def load_training_data():
    # Load training examples from JSON file
    filepath = os.path.join(os.path.dirname(__file__), 'training-data', 'they-them.json')
    with open(filepath, 'r') as f:
        return json.load(f)


def create_training_examples(nlp, training_data):
    # Convert JSON data to spaCy training examples
    examples = []
    debug_count = 0
    
    for item in training_data:
        text = item['text']
        clusters = item['clusters']
        
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
                        found = True
                        break  # Only find first occurrence to avoid duplicates
                
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

def get_latest_model():
    # Find latest fine-tuned model to continue training from
    models_dir = "models"
    if not os.path.exists(models_dir):
        return None
    
    model_dirs = [d for d in os.listdir(models_dir) 
                  if os.path.isdir(os.path.join(models_dir, d)) 
                  and d.startswith("fine_tuned_")]
    
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
        return None


def main():
    print("Loading base model...")
    nlp = spacy.load("en_coreference_web_trf")
    
    # Test base model first
    test_text = "Alex told me that they prefer working from home."
    print(f"\nTesting base model on: '{test_text}'")
    doc = nlp(test_text)
    if doc.spans:
        print(f"Base model found: {[(k, [s.text for s in spans]) for k, spans in doc.spans.items()]}")
    else:
        print("Base model found no clusters")
    
    # Create ONE simple training example manually
    doc = nlp.make_doc(test_text)
    spans = {"coref_clusters_1": [(0, 1), (4, 5)]}  # Alex -> they
    annotations = {"spans": spans}
    example = Example.from_dict(doc, annotations)
    
    print(f"\nCreated manual example with spans: {spans}")
    
    # Minimal training with aggressive learning
    print("Starting minimal training...")
    optimizer = nlp.resume_training()
    
    # Try much higher learning rate
    try:
        optimizer.learn_rate = 1e-2  # Much higher
        print(f"Set learning rate to: {optimizer.learn_rate}")
    except:
        print("Could not set learning rate")
    
    # Try training on WRONG data to see if we can break it
    wrong_doc = nlp.make_doc("The cat sat on the mat")
    wrong_spans = {"coref_clusters_1": [(0, 1), (2, 3)]}  # cat -> sat (wrong!)
    wrong_annotations = {"spans": wrong_spans}
    wrong_example = Example.from_dict(wrong_doc, wrong_annotations)
    
    print("\nTrying to break model with wrong training data...")
    for i in range(20):  # Many iterations of wrong data
        losses = {}
        try:
            nlp.update([wrong_example], sgd=optimizer, losses=losses)
            if i < 5 or i % 5 == 0:
                print(f"Iteration {i+1}: losses = {losses}")
                
        except Exception as e:
            print(f"Error in iteration {i+1}: {e}")
    
    # Now test if anything changed
    print(f"\nTesting after corrupting training:")
    for test in ["The cat sat on the mat", "Alex told me that they work"]:
        doc_test = nlp(test)
        if doc_test.spans:
            print(f"'{test}' -> {[(k, [s.text for s in spans]) for k, spans in doc_test.spans.items()]}")
        else:
            print(f"'{test}' -> No clusters")
    
    # Test after training
    print(f"\nTesting after training:")
    doc_after = nlp(test_text)
    if doc_after.spans:
        print(f"After training found: {[(k, [s.text for s in spans]) for k, spans in doc_after.spans.items()]}")
    else:
        print("After training found no clusters")
    
    # Save & test different sentence
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"models/minimal_{timestamp}"
    os.makedirs("models", exist_ok=True)
    nlp.to_disk(model_path)
    print(f"\nModel saved to: {model_path}")


if __name__ == "__main__":
    main()
    
    
