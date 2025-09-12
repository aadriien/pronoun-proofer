###############################################################################
##  `fine_tune_model.py`                                                     ##
##                                                                           ##
##  Purpose: Incrementally fine-tune spaCy coreference model                 ##
###############################################################################


import spacy
from spacy.tokens import DocBin
from spacy.training import Example
import random
import warnings
import json
import sys
import os


# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Suppress torch CUDA warnings
warnings.filterwarnings("ignore", message=".*torch.cuda.amp.autocast.*")
import tempfile
import os
from pathlib import Path


# Use same model name from src/nlp.py
MODEL_NAME = "en_coreference_web_trf"

# Pronoun groups from existing src/nlp.py
PRONOUN_GROUPS = {
    "he": ["he", "him", "his", "himself"],
    "she": ["she", "her", "hers", "herself"],
    "they": ["they", "them", "their", "theirs", "themself"],
    "it": ["it", "its", "itself"],
    "xe": ["xe", "xem", "xir", "xyr", "xirs", "xyrs", "xemself"],
    "ze": ["ze", "zir", "hir", "zirs", "hirs", "zirself", "hirself"],
    "fae": ["fae", "faer", "faers", "faerself"],
    "ey": ["ey", "em", "eir", "eirs", "emself"],
}


def load_base_model():
    # Load the base coreference model and test it works
    print(f"Loading base model: {MODEL_NAME}")
    try:
        nlp = spacy.load(MODEL_NAME)
        print(f"Successfully loaded {MODEL_NAME}")
        return nlp
    except OSError as e:
        print(f"Error loading model: {e}")
        return None


def test_model_with_example(nlp):
    # Simple test text with clear coreference
    test_text = (
        "John went to the store. He bought some groceries. "
        "Sarah called John later. She asked him about dinner plans."
    )
    
    print("\n" + "="*60)
    print("TESTING BASE MODEL")
    print("="*60)
    print(f"Input text: {test_text}")
    print("\n")
    
    # Process text
    doc = nlp(test_text)
    
    # Print coreference clusters
    if doc.spans:
        print("Coreference clusters found:")
        for cluster_key in doc.spans:
            spans = doc.spans[cluster_key]
            cluster_texts = [span.text for span in spans]
            print(f"  {cluster_key}: {cluster_texts}")
    else:
        print("No coreference clusters found")
    
    return doc


def load_training_data(filename):
    # Load training data from JSON file
    filepath = os.path.join(os.path.dirname(__file__), 'training-data', filename)
    with open(filepath, 'r') as f:
        return json.load(f)


def save_model_version(nlp, version_name):
    # Save model to versioned directory
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, version_name)
    nlp.to_disk(model_path)
    print(f"Model saved to: {model_path}")
    return model_path


def load_model_version(version_name):
    # Load model from versioned directory
    model_path = os.path.join(os.path.dirname(__file__), 'models', version_name)
    if os.path.exists(model_path):
        nlp = spacy.load(model_path)
        print(f"Model loaded from: {model_path}")
        return nlp
    else:
        print(f"Model version {version_name} not found")
        return None


def list_model_versions():
    # List available model versions
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    if os.path.exists(models_dir):
        versions = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
        return sorted(versions)
    return []


def create_coref_annotations(text, clusters):
    # Create span annotations for coreference clusters
    # clusters format: [["Alex", "they"], ["Jordan", "xe", "xir"]]

    spans = {}
    cluster_id = 1
    
    for cluster in clusters:
        span_list = []
        for mention in cluster:
            # Find all occurrences of this mention in text (case insensitive)
            text_lower = text.lower()
            mention_lower = mention.lower()
            start = 0
            
            while True:
                pos = text_lower.find(mention_lower, start)
                if pos == -1:
                    break
                    
                # Check word boundaries to avoid partial matches
                if (pos == 0 or not text[pos-1].isalnum()) and \
                   (pos + len(mention) == len(text) or not text[pos + len(mention)].isalnum()):
                    span_list.append((pos, pos + len(mention)))
                
                start = pos + 1
        
        if span_list:
            spans[f"coref_clusters_{cluster_id}"] = span_list
            cluster_id += 1
    
    return {"spans": spans}


def simple_fine_tune(nlp, training_examples, iterations=1, learning_rate=0.001):
    # Simple fine-tuning with span-annotated examples
    # training_examples format: [{"text": "...", "clusters": [["name", "pronoun"]]}]
    
    print(f"Starting fine-tuning with {len(training_examples)} examples")
    print(f"Learning rate: {learning_rate}, Iterations: {iterations}")
    
    # Create optimizer with lower learning rate
    optimizer = nlp.create_optimizer()
    optimizer.learn_rate = learning_rate
    
    for i in range(iterations):
        print(f"Training iteration {i+1}/{iterations}")
        
        for example_data in training_examples:
            text = example_data["text"]
            clusters = example_data.get("clusters", [])
            
            # Create span annotations
            annotations = create_coref_annotations(text, clusters)
            
            # Create training example with annotations
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            
            # Update model
            nlp.update([example], sgd=optimizer)
    
    print("Fine-tuning complete")
    return nlp


def test_before_after(original_nlp, updated_nlp, test_text):
    # Compare model performance before and after fine-tuning
    print(f"\nTesting: {test_text}")
    
    print("\nBEFORE fine-tuning:")
    doc_before = original_nlp(test_text)
    if doc_before.spans:
        for cluster_key in doc_before.spans:
            spans = doc_before.spans[cluster_key]
            print(f"  {cluster_key}: {[span.text for span in spans]}")
    else:
        print("  No clusters found")
    
    print("\nAFTER fine-tuning:")
    doc_after = updated_nlp(test_text)
    if doc_after.spans:
        for cluster_key in doc_after.spans:
            spans = doc_after.spans[cluster_key]
            print(f"  {cluster_key}: {[span.text for span in spans]}")
    else:
        print("  No clusters found")



def main():
    print("Starting spaCy coreference model fine-tuning setup...")
    
    # Step 1: Load base model
    nlp = load_base_model()
    if nlp is None:
        print("Cannot proceed without base model. Exiting.")
        return
    
    # Step 2: Test with example
    doc = test_model_with_example(nlp)
    
    # Step 3: Test simple fine-tuning
    print("\n" + "="*60)
    print("TESTING SIMPLE FINE-TUNING")
    print("="*60)
    
    # Load training data from JSON file
    training_examples = load_training_data('they-them.json')
    
    test_text = "Blake is a talented artist. They create sculptures from recycled materials."
    
    # Show existing model versions & decide which to use
    existing_versions = list_model_versions()
    
    # Option to continue from latest model or start fresh
    use_latest = True  # Set to False to always start from base model
    
    if use_latest and existing_versions:
        latest_version = existing_versions[-1]
        print(f"Continuing from latest model: {latest_version}")
        print(f"Other versions available: {existing_versions[:-1]}")
        
        # Load latest model to continue training
        nlp_to_train = load_model_version(latest_version)
        if nlp_to_train is None:
            print("Failed to load latest model, using base model")
            nlp_to_train = nlp
    else:
        print("Starting fresh from base model")
        nlp_to_train = nlp
    
    # Keep original model for comparison
    original_nlp = spacy.load(MODEL_NAME)
    
    # Fine-tune with many more iterations & lower learning rate
    updated_nlp = simple_fine_tune(nlp_to_train, training_examples, iterations=300, learning_rate=0.0001)
    
    # Save updated model with timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    version_name = f"they_them_{timestamp}"
    save_model_version(updated_nlp, version_name)
    
    # Compare results
    test_before_after(original_nlp, updated_nlp, test_text)
    
    print("\n" + "="*60)
    print("FINE-TUNING TEST COMPLETE")
    print("="*60)
    print("Ready for experimentation with different training examples")


if __name__ == "__main__":
    main()
    
    
