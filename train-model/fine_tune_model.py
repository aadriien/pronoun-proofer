###############################################################################
##  `fine_tune_model.py`                                                     ##
##                                                                           ##
##  Purpose: Incrementally fine-tune spaCy coreference model                 ##
###############################################################################


import warnings
warnings.filterwarnings("ignore")

import os
import json
import spacy

from spacy.training import Example
from datetime import datetime


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


def run_one_example(nlp):
    training_data = [
        {
            "text": "Alex told me that they prefer working from home because it gives them more flexibility with their schedule.",
            "clusters": [["Alex", "they", "them", "their"]]
        }
    ]

    # Test base model first
    test_text = training_data["text"]
    print(f"\nTesting base model on: '{test_text}'")

    doc = nlp(test_text)
    if doc.spans:
        print(f"Base model found: {[(k, [s.text for s in spans]) for k, spans in doc.spans.items()]}")
    else:
        print("Base model found no clusters")
    
    # Create simple training example manually
    examples = create_training_examples(nlp, training_data)
    print("\n\n")

    coref = nlp.get_pipe("coref")
    optimizer = nlp.resume_training()
    
    losses = {}
    coref.update(examples, sgd=optimizer, losses=losses)
    print(losses)

    print("\n\n")

    # coref = nlp.add_pipe("experimental_coref")
    # optimizer = nlp.initialize() 
    # losses = coref.update(examples, sgd=optimizer)

    # print(losses)
    # print("\n\n")


def train_several_examples(nlp, training_data):
    examples = create_training_examples(nlp, training_data)
    print("\n\n")

    optimizer = nlp.resume_training() 
    optimizer.learn_rate = 1e-4

    # Fine-tune 1 example at a time
    n_passes = 30
    for epoch in range(n_passes):
        losses = {}
        for example in examples:
            nlp.update([example], sgd=optimizer, losses=losses)

        print(f"Epoch {epoch+1}, losses: {losses}")

    print("\n\n")


def test_after_training(nlp, training_data):
    print(f"\nTesting after training:")

    doc_after = nlp(training_data[0]["text"])

    for example in training_data:
        doc_after = nlp(example["text"])

        if doc_after.spans:
            print(f"After training found: {[(k, [s.text for s in spans]) for k, spans in doc_after.spans.items()]}")
        else:
            print("After training found no clusters")
    

def main():
    print("Loading base model...")
    nlp = spacy.load("en_coreference_web_trf")

    # Try with just 1 instance (see effect of initialize vs update)
    # run_one_example(nlp, training_data[0])

    # Train with multiple examples from JSON
    training_data = load_training_data()
    train_several_examples(nlp, training_data)

    # Test results
    test_after_training(nlp, training_data)


    # # Save & test different sentence
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # model_path = f"models/minimal_{timestamp}"
    # os.makedirs("models", exist_ok=True)
    # nlp.to_disk(model_path)
    # print(f"\nModel saved to: {model_path}")


if __name__ == "__main__":
    main()
    
    
