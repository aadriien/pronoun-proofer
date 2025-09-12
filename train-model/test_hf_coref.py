###############################################################################
##  `test_hf_coref.py`                                                       ##
##                                                                           ##
##  Purpose: Test Hugging Face coreference model with basic examples        ##
###############################################################################


import warnings
warnings.filterwarnings("ignore")
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)

from transformers import AutoTokenizer, AutoModel, AutoConfig
from transformers import pipeline
import torch


def test_hf_coreference():
    print("Testing Hugging Face coreference models...")
    
    # Test examples
    test_examples = [
        "John went to the store. He bought some groceries.",
        "Alex told me that they prefer working from home.",
        "Sarah is a doctor. She works at the hospital.",
        "The cat sat on the mat. It was comfortable."
    ]
    
    # Try actual coreference models
    coreference_models = [
        "biu-nlp/f-coref",
        "coref-data/spanbert_hf_base",
        "patrickvonplaten/longformer-coreference-ontonotes"
    ]
    
    for model_name in coreference_models:
        print(f"\nTrying coreference model: {model_name}")
        
        try:
            # Load the actual coreference model with its custom components
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            config = AutoConfig.from_pretrained(model_name)
            
            # Try to load with custom modeling if available
            try:
                from transformers import AutoModelForTokenClassification
                model = AutoModelForTokenClassification.from_pretrained(model_name)
                print(f"Loaded as TokenClassification model")
            except:
                model = AutoModel.from_pretrained(model_name)
                print(f"Loaded as base model")
            
            print(f"Successfully loaded {model_name}")
            
            # Test actual coreference resolution
            test_coreference_resolution(model, tokenizer, test_examples)
            
            break  # If successful, stop trying other models
            
        except Exception as e:
            print(f"Failed to load {model_name}: {e}")
            continue
    
    else:
        print("\nAll coreference models failed. Trying neuralcoref approach...")
        try_neuralcoref()


def test_coreference_resolution(model, tokenizer, test_examples):
    print("\nTesting actual coreference resolution:")
    
    for i, text in enumerate(test_examples, 1):
        print(f"\n{i}. Text: '{text}'")
        
        try:
            # Tokenize input
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            # Get model predictions
            with torch.no_grad():
                outputs = model(**inputs)
                
            # Check what the model outputs
            if hasattr(outputs, 'logits'):
                logits = outputs.logits
                print(f"   Model output shape: {logits.shape}")
                
                # Try to interpret as token classifications
                if len(logits.shape) == 3:  # [batch, seq_len, num_classes]
                    predictions = torch.argmax(logits, dim=-1)
                    print(f"   Token predictions: {predictions[0].tolist()[:10]}...")  # First 10
                    
                    # Check if any tokens are classified as mentions/entities
                    unique_preds = torch.unique(predictions)
                    print(f"   Unique prediction classes: {unique_preds.tolist()}")
                    
                    # If we have non-zero predictions, there might be mentions detected
                    non_zero_count = torch.sum(predictions != 0).item()
                    if non_zero_count > 0:
                        print(f"   Found {non_zero_count} potential mention tokens")
                    else:
                        print(f"   No mentions detected")
                        
            else:
                print(f"   Model output type: {type(outputs)}")
                print(f"   Available attributes: {dir(outputs)}")
                
        except Exception as e:
            print(f"   Error processing: {e}")

def try_neuralcoref():
    print("\nTrying neuralcoref (spaCy extension)...")
    
    try:
        import spacy
        import neuralcoref
        
        # Load English model
        nlp = spacy.load('en_core_web_sm')
        neuralcoref.add_to_pipe(nlp)
        
        test_examples = [
            "John went to the store. He bought some groceries.",
            "Alex told me that they prefer working from home.",
            "Sarah is a doctor. She works at the hospital."
        ]
        
        print("Testing neuralcoref:")
        for i, text in enumerate(test_examples, 1):
            print(f"\n{i}. Text: {text}")
            doc = nlp(text)
            
            if doc._.has_coref:
                print(f"   Clusters: {doc._.coref_clusters}")
                print(f"   Resolved: {doc._.coref_resolved}")
            else:
                print("   No coreferences found")
        
    except ImportError:
        print("neuralcoref not installed. Install with: pip install neuralcoref")
    except Exception as e:
        print(f"neuralcoref failed: {e}")


if __name__ == "__main__":
    test_hf_coreference()

