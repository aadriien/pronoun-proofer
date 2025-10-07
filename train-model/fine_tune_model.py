###############################################################################
##  `fine_tune_model.py`                                                     ##
##                                                                           ##
##  Purpose: Incrementally fine-tune spaCy coreference model                 ##
###############################################################################


import random

import warnings
warnings.filterwarnings("ignore")

from model_utils import (
    THEY_THEM_DATA, NEOPRONOUNS_DATA,
    load_training_data, create_training_examples, 
    load_base_model, get_latest_model, save_model_version
)


def run_one_example(nlp, training_data):
    # Test base model first
    test_text = training_data["text"]
    print(f"\nTesting base model on: '{test_text}'")

    doc = nlp(test_text)
    if doc.spans:
        print(f"Base model found: {[(k, [s.text for s in spans]) for k, spans in doc.spans.items()]}")
    else:
        print("Base model found no clusters")
    
    # Create simple training example manually
    examples = create_training_examples(nlp, [training_data])
    print("\n")

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


def train_several_examples(nlp, training_data, n_passes = 15, learn = 1e-7, drop = 0.5):
    examples = create_training_examples(nlp, training_data)
    print("\n")

    print(f"Resuming training with configs:\n")
    print(f"    Epochs (passes): {n_passes}")
    print(f"    Learn rate: {learn}")
    print(f"    Dropout: {drop}")
    print("\n")

    optimizer = nlp.resume_training() 
    optimizer.learn_rate = learn

    for epoch in range(n_passes):
        # Shuffle to improve generalization
        random.shuffle(examples)
        losses = {}

        # Fine-tune 1 example at a time
        for example in examples:
            nlp.update([example], drop=drop, sgd=optimizer, losses=losses)

        print(f"Epoch {epoch+1}, losses: {losses}")

    print("\n\n")


def test_after_training(nlp, training_data):
    # print(f"\nTesting after training:")

    for example in training_data:
        doc_after = nlp(example["text"])

        if doc_after.spans:
            print(f"After training found: {[(k, [s.text for s in spans]) for k, spans in doc_after.spans.items()]}")
        else:
            print("After training found no clusters")


def main():
    # print("Checking for latest model...")
    # nlp = get_latest_model()
    
    # if nlp is None:
    #     print("No fine-tuned model found, loading base model...")
    #     nlp = load_base_model()

    nlp = load_base_model()

    # Try with just 1 instance (see effect of initialize vs update)
    # run_one_example(nlp, training_data[0])

    # Train with multiple examples from JSON
    training_data = load_training_data(json_file=THEY_THEM_DATA)

    # # Test results from baseline model (no fine-tuning applied)
    # print("\n\nTesting RESULTS from the BASE coref model:\n")
    # test_after_training(nlp, training_data)

    
    train_several_examples(nlp, training_data, n_passes=15, learn=1e-7, drop=0.4)

    # training_data = load_training_data(json_file=NEOPRONOUNS_DATA)
    # train_several_examples(nlp, training_data, n_passes=5, learn=1e-8, drop=0.5)

    # Test results
    print("\n\nTesting RESULTS from the FINE-TUNED coref model:\n")
    test_after_training(nlp, training_data)

    # Save & test different sentence
    model_path = save_model_version(nlp, trained_on_dir=THEY_THEM_DATA)
    # model_path = save_model_version(nlp, trained_on_dir=NEOPRONOUNS_DATA)


    # for item in training_data:
    #     run_one_example(nlp, item)


if __name__ == "__main__":
    main()
    
    
