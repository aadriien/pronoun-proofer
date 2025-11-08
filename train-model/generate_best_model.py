###############################################################################
##  `generate_best_model.py`                                                 ##
##                                                                           ##
##  Purpose: Iterative hyperparameter optimization for coreference model     ##
###############################################################################


import random
import json
import os
import time
from datetime import datetime
from itertools import product
import numpy as np

from model_utils import (
    THEY_THEM_DATA, NEOPRONOUNS_DATA,
    load_training_data, create_training_examples,
    load_base_model, save_model_version
)
from evaluate_model import CoreferenceEvaluator
from fine_tune_model import train_several_examples




def comprehensive_optimization():
    """Comprehensive optimization testing many parameter combinations"""
    print("Comprehensive Model Optimization - Finding Best Configuration")
    print("=" * 60)
    
    # Load ALL available pronoun training data
    they_them_data = load_training_data(json_file=THEY_THEM_DATA)
    neopronoun_data = load_training_data(json_file=NEOPRONOUNS_DATA)
    
    print(f"They/them examples: {len(they_them_data)}")
    print(f"Neopronoun examples: {len(neopronoun_data)}")
    
    # Use ALL data + emphasize neopronouns (completely new to the model)
    combined_data = they_them_data + neopronoun_data * 3  # 3x neopronouns for emphasis
    print(f"Total training examples: {len(combined_data)} (includes 3x neopronoun repetition)")
    
    base_nlp = load_base_model()
    if not base_nlp:
        print("Failed to load base model")
        return
    
    # Optimized for learning new pronouns while preserving existing clustering knowledge
    param_combinations = [
        # Standard 1e-7 range with proper regularization
        {'n_passes': 30, 'learn_rate': 1e-7, 'dropout': 0.5, 'batch_size': 4},  # balanced
        {'n_passes': 35, 'learn_rate': 1e-7, 'dropout': 0.4, 'batch_size': 4},  # more training
        {'n_passes': 25, 'learn_rate': 1e-7, 'dropout': 0.6, 'batch_size': 4},  # high regularization
        
        # Conservative but thorough - good for new vocabulary
        {'n_passes': 40, 'learn_rate': 8e-8, 'dropout': 0.4, 'batch_size': 4},
        {'n_passes': 50, 'learn_rate': 6e-8, 'dropout': 0.3, 'batch_size': 4},
        {'n_passes': 60, 'learn_rate': 5e-8, 'dropout': 0.3, 'batch_size': 4},
        
        # Gentle long training for vocabulary acquisition
        {'n_passes': 45, 'learn_rate': 7e-8, 'dropout': 0.4, 'batch_size': 4},
        {'n_passes': 35, 'learn_rate': 9e-8, 'dropout': 0.4, 'batch_size': 4},
        
        # Test batch effects on clustering quality
        {'n_passes': 30, 'learn_rate': 1e-7, 'dropout': 0.5, 'batch_size': 2},  # smaller batches
        {'n_passes': 30, 'learn_rate': 1e-7, 'dropout': 0.5, 'batch_size': 6},  # larger batches
        
        # Very conservative for stability
        {'n_passes': 80, 'learn_rate': 3e-8, 'dropout': 0.2, 'batch_size': 4},
        {'n_passes': 70, 'learn_rate': 4e-8, 'dropout': 0.3, 'batch_size': 4},
    ]
    
    print(f"Will test {len(param_combinations)} different configurations")
    
    best_score = -1
    best_params = None
    best_model = None
    results = []
    
    evaluator = CoreferenceEvaluator()
    
    for i, params in enumerate(param_combinations, 1):
        print(f"\n=== Testing Configuration {i}/3 ===")
        print(f"Params: {params}")
        
        try:
            # Load fresh model
            nlp = load_base_model()
            if not nlp:
                print("Failed to load base model")
                continue
            
            # Train on ALL pronoun data (they/them + neopronouns)
            print(f"  Training on {len(combined_data)} examples with batch processing...")
            train_several_examples(
                nlp, 
                combined_data,  # Use ALL pronoun data
                n_passes=params['n_passes'],
                learn=params['learn_rate'],
                drop=params['dropout'],
                batch_size=params['batch_size']
            )
            
            # Evaluate on a test subset (different from training)
            test_data = they_them_data[100:150] + neopronoun_data  # Mix for evaluation
            score = evaluator.evaluate_model(nlp, test_data, 0, len(combined_data), sample_size=len(test_data))
            
            print(f"  Score: {score:.4f}")
            evaluator.print_evaluation_summary(verbose=False)
            
            metrics = evaluator.get_detailed_metrics()
            results.append({
                'params': params,
                'score': score,
                'model': nlp,
                'metrics': metrics
            })
            
            if score > best_score:
                best_score = score
                best_params = params
                best_model = nlp
                print(f"  New best score: {best_score:.4f}")
            
        except Exception as e:
            print(f"  Configuration failed: {e}")
            continue
    
    # Results summary
    print(f"\n{'='*50}")
    print("OPTIMIZATION RESULTS")
    print(f"{'='*50}")
    print(f"Configurations tested: {len(results)}")
    
    if results:
        print(f"Best score: {best_score:.4f}")
        print(f"Best params: {best_params}")
        
        # Save best model
        if best_model:
            model_path = save_model_version(best_model, trained_on_dir="optimized")
            print(f"Best model saved to: {model_path}")
        
        # Show all results
        print("\nAll Results:")
        for i, result in enumerate(sorted(results, key=lambda x: x['score'], reverse=True), 1):
            print(f"{i}. Score: {result['score']:.4f} | {result['params']}")
    else:
        print("No successful configurations")


def main():
    comprehensive_optimization()


if __name__ == "__main__":
    main()