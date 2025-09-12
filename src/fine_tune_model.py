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


def simple_fine_tune(nlp, training_examples, iterations=1):
    # Simple fine-tuning with span-annotated examples
    # training_examples format: [{"text": "...", "clusters": [["name", "pronoun"]]}]
    
    print(f"Starting fine-tuning with {len(training_examples)} examples")
    
    optimizer = nlp.create_optimizer()
    
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
    
    # Focused training data for singular they/them
    training_examples = [
        {
            "text": "Alex is a great student. They study hard every day.",
            "clusters": [["Alex", "They"]]
        },
        {
            "text": "Jordan loves music. They play guitar beautifully.",
            "clusters": [["Jordan", "They"]]
        },
        {
            "text": "Sam works downtown. They commute by train.",
            "clusters": [["Sam", "They"]]
        },
        {
            "text": "Riley is my friend. They help me with homework.",
            "clusters": [["Riley", "They"]]
        },
        {
            "text": "Casey joined our team. They bring fresh ideas.",
            "clusters": [["Casey", "They"]]
        },
        {
            "text": "Morgan loves cooking. They make amazing pasta.",
            "clusters": [["Morgan", "They"]]
        },
        {
            "text": "Taylor is very creative. They design beautiful websites.",
            "clusters": [["Taylor", "They"]]
        },
        {
            "text": "Avery studies biology. They want to be a doctor.",
            "clusters": [["Avery", "They"]]
        },
        {
            "text": "Quinn loves reading. They finish two books per week.",
            "clusters": [["Quinn", "They"]]
        },
        {
            "text": "Devon plays soccer. They practice every afternoon.",
            "clusters": [["Devon", "They"]]
        }
    ]
    
    test_text = "Blake is a talented artist. They create sculptures from recycled materials."
    
    # Make copy of original model for comparison
    original_nlp = spacy.load(MODEL_NAME)
    
    # Fine-tune the model with more iterations
    updated_nlp = simple_fine_tune(nlp, training_examples, iterations=5)
    
    # Compare results
    test_before_after(original_nlp, updated_nlp, test_text)
    
    print("\n" + "="*60)
    print("FINE-TUNING TEST COMPLETE")
    print("="*60)
    print("Ready for experimentation with different training examples")


if __name__ == "__main__":
    main()
    
    
