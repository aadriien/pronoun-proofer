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
    
    # Load training data
    training_data = load_training_data(json_file=THEY_THEM_DATA)
    print(f"Loaded {len(training_data)} training examples")
    
    # Generate training examples ONCE - this is expensive
    print("Generating training examples (this may take a moment)...")
    base_nlp = load_base_model()
    if not base_nlp:
        print("Failed to load base model")
        return
    
    # Use more data for better optimization
    subset_data = training_data[:50]  # Increased from 30
    training_examples = create_training_examples(base_nlp, subset_data)
    print(f"Generated {len(training_examples)} training examples\n")
    
    # Focus on optimal range: LR 5e-8 to 5e-7, epochs 15-30, dropout 0.3-0.5
    param_combinations = [
        # Sweet spot variations around best performers
        {'n_passes': 15, 'learn_rate': 5e-7, 'dropout': 0.5, 'batch_size': 4},  # Best from previous
        {'n_passes': 18, 'learn_rate': 3e-7, 'dropout': 0.45, 'batch_size': 4},
        {'n_passes': 20, 'learn_rate': 2e-7, 'dropout': 0.4, 'batch_size': 4},
        {'n_passes': 22, 'learn_rate': 1e-7, 'dropout': 0.4, 'batch_size': 4},
        {'n_passes': 25, 'learn_rate': 8e-8, 'dropout': 0.35, 'batch_size': 4},
        {'n_passes': 28, 'learn_rate': 6e-8, 'dropout': 0.3, 'batch_size': 4},
        {'n_passes': 30, 'learn_rate': 5e-8, 'dropout': 0.3, 'batch_size': 4},
        
        # Explore slightly higher LR with more regularization
        {'n_passes': 12, 'learn_rate': 7e-7, 'dropout': 0.6, 'batch_size': 4},
        {'n_passes': 15, 'learn_rate': 4e-7, 'dropout': 0.55, 'batch_size': 4},
        
        # Test batch size variations with optimal LR range
        {'n_passes': 20, 'learn_rate': 1e-7, 'dropout': 0.4, 'batch_size': 2},
        {'n_passes': 20, 'learn_rate': 1e-7, 'dropout': 0.4, 'batch_size': 6},
        {'n_passes': 20, 'learn_rate': 1e-7, 'dropout': 0.4, 'batch_size': 8},
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
            
            # Use the working training function from fine_tune_model.py with the subset data
            print(f"  Training with working batch processing...")
            train_several_examples(
                nlp, 
                subset_data,  # Use the subset we prepared
                n_passes=params['n_passes'],
                learn=params['learn_rate'],
                drop=params['dropout'],
                batch_size=params['batch_size']
            )
            
            # Values for evaluation
            total_loss = 100.0  # Will be calculated properly by evaluator
            examples_processed = len(subset_data)
            
            # Evaluate the model using the same subset we trained on
            score = evaluator.evaluate_model(nlp, subset_data, total_loss, examples_processed, sample_size=len(subset_data))
            
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