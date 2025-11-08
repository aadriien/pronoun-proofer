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


class HyperparameterOptimizer:
    def __init__(self):
        # Define parameter search spaces
        self.param_space = {
            'n_passes': [5, 10, 15, 20],
            'learn_rate': [1e-8, 5e-8, 1e-7, 5e-7, 1e-6],
            'dropout': [0.3, 0.4, 0.5, 0.6],
            'batch_size': [2, 4, 6, 8]
        }
        
        # Results tracking
        self.results = []
        self.best_score = -float('inf')
        self.best_params = None
        self.best_model_path = None
        
        # Results file
        self.results_file = os.path.join(os.path.dirname(__file__), "optimization_results.json")
        
        # Evaluator instance
        self.evaluator = CoreferenceEvaluator()
        
    def load_previous_results(self):
        """Load results from previous optimization runs"""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r') as f:
                    data = json.load(f)
                    self.results = data.get('results', [])
                    self.best_score = data.get('best_score', -float('inf'))
                    self.best_params = data.get('best_params', None)
                    self.best_model_path = data.get('best_model_path', None)
                print(f"Loaded {len(self.results)} previous results")
                if self.best_params:
                    print(f"Current best score: {self.best_score:.4f} with params: {self.best_params}")
            except Exception as e:
                print(f"Could not load previous results: {e}")
    
    def save_results(self):
        """Save current results to file"""
        data = {
            'results': self.results,
            'best_score': self.best_score,
            'best_params': self.best_params,
            'best_model_path': self.best_model_path,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.results_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def train_and_evaluate(self, params, training_data):
        """Train model with given parameters and return evaluation score"""
        print(f"\nTraining with params: {params}")
        
        # Load fresh base model
        nlp = load_base_model()
        if nlp is None:
            print("Failed to load base model")
            return 0.0
        
        optimizer = nlp.resume_training()
        optimizer.learn_rate = params['learn_rate']
        
        total_loss = 0.0
        examples_processed = 0
        
        # Training loop with gradient accumulation
        for epoch in range(params['n_passes']):
            random.shuffle(training_data)
            epoch_losses = {}
            batches_processed = 0
            
            for i in range(0, len(training_data), params['batch_size']):
                batch_data = training_data[i:i + params['batch_size']]
                batch_losses = {}
                successful_updates = 0
                
                # Process each item in batch
                for item in batch_data:
                    individual_examples = create_training_examples(nlp, [item])
                    
                    if individual_examples:
                        for example in individual_examples:
                            try:
                                single_losses = {}
                                nlp.update([example], drop=params['dropout'], sgd=None, losses=single_losses)
                                
                                # Accumulate losses
                                for key, value in single_losses.items():
                                    if key in batch_losses:
                                        batch_losses[key] += value
                                    else:
                                        batch_losses[key] = value
                                successful_updates += 1
                            except Exception:
                                continue
                
                # Apply accumulated gradients
                if successful_updates > 0:
                    try:
                        optimizer.step_schedules()
                        batches_processed += 1
                        examples_processed += successful_updates
                        
                        # Accumulate epoch losses
                        for key, value in batch_losses.items():
                            if key in epoch_losses:
                                epoch_losses[key] += value
                            else:
                                epoch_losses[key] = value
                    except Exception:
                        continue
            
            # Track total loss for scoring
            if 'coref' in epoch_losses:
                total_loss += epoch_losses['coref']
        
        # Evaluate model performance using the dedicated evaluator
        score = self.evaluator.evaluate_model(nlp, training_data, total_loss, examples_processed, sample_size=30)
        metrics = self.evaluator.get_detailed_metrics()
        
        # Print compact evaluation summary
        print(f"  Final score: {score:.4f}")
        self.evaluator.print_evaluation_summary(verbose=False)
        
        return score, nlp
    
    def random_search(self, training_data, n_trials=20):
        """Perform random search optimization"""
        print(f"\nStarting random search with {n_trials} trials...")
        
        for trial in range(n_trials):
            print(f"\n=== Trial {trial + 1}/{n_trials} ===")
            
            # Sample random parameters
            params = {
                'n_passes': random.choice(self.param_space['n_passes']),
                'learn_rate': random.choice(self.param_space['learn_rate']),
                'dropout': random.choice(self.param_space['dropout']),
                'batch_size': random.choice(self.param_space['batch_size'])
            }
            
            # Check if we've already tried this combination
            if any(r['params'] == params for r in self.results):
                print("  Skipping - already tried this combination")
                continue
            
            start_time = time.time()
            
            try:
                score, trained_model = self.train_and_evaluate(params, training_data)
                
                # Save model if it's the best so far
                model_path = None
                if score > self.best_score:
                    print(f"  New best score! {score:.4f} > {self.best_score:.4f}")
                    self.best_score = score
                    self.best_params = params
                    
                    # Save the best model
                    model_path = save_model_version(trained_model, trained_on_dir=f"best_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    self.best_model_path = model_path
                    print(f"  Best model saved to: {model_path}")
                
                # Record result
                result = {
                    'trial': trial + 1,
                    'params': params,
                    'score': score,
                    'model_path': model_path,
                    'duration_minutes': (time.time() - start_time) / 60,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.results.append(result)
                self.save_results()
                
            except Exception as e:
                print(f"  Trial failed: {e}")
                continue
        
        return self.best_params, self.best_score
    
    def grid_search(self, training_data, max_combinations=50):
        """Perform systematic grid search (limited by max_combinations)"""
        print(f"\nStarting grid search (max {max_combinations} combinations)...")
        
        # Generate all parameter combinations
        param_combinations = list(product(
            self.param_space['n_passes'],
            self.param_space['learn_rate'],
            self.param_space['dropout'],
            self.param_space['batch_size']
        ))
        
        # Shuffle and limit combinations
        random.shuffle(param_combinations)
        param_combinations = param_combinations[:max_combinations]
        
        for i, (n_passes, learn_rate, dropout, batch_size) in enumerate(param_combinations):
            print(f"\n=== Grid Search {i + 1}/{len(param_combinations)} ===")
            
            params = {
                'n_passes': n_passes,
                'learn_rate': learn_rate,
                'dropout': dropout,
                'batch_size': batch_size
            }
            
            # Check if already tried
            if any(r['params'] == params for r in self.results):
                print("  Skipping - already tried this combination")
                continue
            
            start_time = time.time()
            
            try:
                score, trained_model = self.train_and_evaluate(params, training_data)
                
                model_path = None
                if score > self.best_score:
                    print(f"  New best score! {score:.4f} > {self.best_score:.4f}")
                    self.best_score = score
                    self.best_params = params
                    
                    model_path = save_model_version(trained_model, trained_on_dir=f"best_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    self.best_model_path = model_path
                    print(f"  Best model saved to: {model_path}")
                
                result = {
                    'trial': i + 1,
                    'params': params,
                    'score': score,
                    'model_path': model_path,
                    'duration_minutes': (time.time() - start_time) / 60,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.results.append(result)
                self.save_results()
                
            except Exception as e:
                print(f"  Grid search step failed: {e}")
                continue
        
        return self.best_params, self.best_score
    
    def bayesian_optimization(self, training_data, n_trials=15):
        """Simple Bayesian optimization using previous results to guide search"""
        print(f"\nStarting Bayesian optimization with {n_trials} trials...")
        
        # If we have previous results, use them to guide the search
        if len(self.results) >= 3:
            print("Using previous results to guide parameter selection...")
            
            # Analyze which parameters tend to work better
            param_scores = {'n_passes': {}, 'learn_rate': {}, 'dropout': {}, 'batch_size': {}}
            
            for result in self.results:
                score = result['score']
                params = result['params']
                
                for param_name, param_value in params.items():
                    if param_value not in param_scores[param_name]:
                        param_scores[param_name][param_value] = []
                    param_scores[param_name][param_value].append(score)
            
            # Calculate average scores for each parameter value
            param_preferences = {}
            for param_name, value_scores in param_scores.items():
                param_preferences[param_name] = {}
                for value, scores in value_scores.items():
                    param_preferences[param_name][value] = np.mean(scores)
            
            print("Parameter preferences based on historical performance:")
            for param_name, prefs in param_preferences.items():
                sorted_prefs = sorted(prefs.items(), key=lambda x: x[1], reverse=True)
                print(f"  {param_name}: {sorted_prefs[:3]}")
        
        for trial in range(n_trials):
            print(f"\n=== Bayesian Trial {trial + 1}/{n_trials} ===")
            
            # Generate parameters with bias toward historically good values
            if len(self.results) >= 3:
                params = self._sample_biased_params(param_preferences)
            else:
                # Random sampling if not enough history
                params = {
                    'n_passes': random.choice(self.param_space['n_passes']),
                    'learn_rate': random.choice(self.param_space['learn_rate']),
                    'dropout': random.choice(self.param_space['dropout']),
                    'batch_size': random.choice(self.param_space['batch_size'])
                }
            
            # Check if already tried
            if any(r['params'] == params for r in self.results):
                print("  Skipping - already tried this combination")
                continue
            
            start_time = time.time()
            
            try:
                score, trained_model = self.train_and_evaluate(params, training_data)
                
                model_path = None
                if score > self.best_score:
                    print(f"  New best score! {score:.4f} > {self.best_score:.4f}")
                    self.best_score = score
                    self.best_params = params
                    
                    model_path = save_model_version(trained_model, trained_on_dir=f"best_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    self.best_model_path = model_path
                    print(f"  Best model saved to: {model_path}")
                
                result = {
                    'trial': trial + 1,
                    'params': params,
                    'score': score,
                    'model_path': model_path,
                    'duration_minutes': (time.time() - start_time) / 60,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.results.append(result)
                self.save_results()
                
            except Exception as e:
                print(f"  Bayesian trial failed: {e}")
                continue
        
        return self.best_params, self.best_score
    
    def _sample_biased_params(self, param_preferences):
        """Sample parameters with bias toward historically good values"""
        params = {}
        
        for param_name, space in self.param_space.items():
            if param_name in param_preferences and param_preferences[param_name]:
                # Create weighted sampling based on historical performance
                values = list(param_preferences[param_name].keys())
                scores = [param_preferences[param_name][v] for v in values]
                
                # Convert scores to probabilities (higher score = higher probability)
                min_score = min(scores) if scores else 0
                adjusted_scores = [s - min_score + 0.1 for s in scores]  # Add small constant
                total = sum(adjusted_scores)
                probabilities = [s / total for s in adjusted_scores]
                
                # Sample based on probabilities
                params[param_name] = np.random.choice(values, p=probabilities)
            else:
                # Random sampling if no historical data
                params[param_name] = random.choice(space)
        
        return params
    
    def print_summary(self):
        """Print optimization summary"""
        if not self.results:
            print("\nNo results to summarize.")
            return
        
        print(f"\n{'='*60}")
        print("HYPERPARAMETER OPTIMIZATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total trials completed: {len(self.results)}")
        print(f"Best score achieved: {self.best_score:.4f}")
        print(f"Best parameters: {self.best_params}")
        print(f"Best model saved to: {self.best_model_path}")
        
        # Show top 5 results with more details
        sorted_results = sorted(self.results, key=lambda x: x['score'], reverse=True)[:5]
        print(f"\nTop 5 Results:")
        print("-" * 100)
        print(f"{'Rank':<4} {'Score':<8} {'Duration':<10} {'Epochs':<7} {'LR':<10} {'Dropout':<8} {'Batch':<6}")
        print("-" * 100)
        for i, result in enumerate(sorted_results, 1):
            params = result['params']
            duration = result.get('duration_minutes', 0)
            print(f"{i:<4} {result['score']:<8.4f} {duration:<10.1f} {params['n_passes']:<7} {params['learn_rate']:<10.0e} {params['dropout']:<8.1f} {params['batch_size']:<6}")
        
        # Show parameter analysis
        if len(self.results) >= 5:
            print(f"\nParameter Analysis:")
            print("-" * 40)
            
            param_analysis = {'n_passes': {}, 'learn_rate': {}, 'dropout': {}, 'batch_size': {}}
            
            for result in self.results:
                score = result['score']
                params = result['params']
                
                for param_name, param_value in params.items():
                    if param_value not in param_analysis[param_name]:
                        param_analysis[param_name][param_value] = []
                    param_analysis[param_name][param_value].append(score)
            
            for param_name, value_scores in param_analysis.items():
                if value_scores:
                    avg_scores = {v: np.mean(scores) for v, scores in value_scores.items()}
                    best_value = max(avg_scores.keys(), key=lambda x: avg_scores[x])
                    print(f"{param_name:12}: {best_value} (avg score: {avg_scores[best_value]:.4f})")


def test_evaluation_system():
    """Test the evaluation system with base model"""
    print("Testing evaluation system with base model...")
    
    # Load test data and base model
    test_data = load_training_data(json_file=THEY_THEM_DATA)[:10]
    nlp = load_base_model()
    
    if nlp and test_data:
        evaluator = CoreferenceEvaluator()
        score = evaluator.evaluate_model(nlp, test_data, sample_size=10)
        
        print(f"\nBase model evaluation:")
        print(f"Composite Score: {score:.4f}")
        evaluator.print_evaluation_summary()
    else:
        print("Failed to load model or data for testing")


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
    
    # Focus on parameters that actually make a difference
    param_combinations = [
        # Conservative learning rate with extended training
        {'n_passes': 25, 'learn_rate': 1e-8, 'dropout': 0.3, 'batch_size': 4},
        {'n_passes': 30, 'learn_rate': 5e-9, 'dropout': 0.3, 'batch_size': 4},
        {'n_passes': 40, 'learn_rate': 1e-9, 'dropout': 0.2, 'batch_size': 4},
        
        # Medium learning rates with substantial training
        {'n_passes': 20, 'learn_rate': 5e-8, 'dropout': 0.4, 'batch_size': 4},
        {'n_passes': 25, 'learn_rate': 1e-7, 'dropout': 0.4, 'batch_size': 4},
        {'n_passes': 30, 'learn_rate': 1e-7, 'dropout': 0.3, 'batch_size': 4},
        
        # Aggressive learning rates with careful training
        {'n_passes': 15, 'learn_rate': 5e-7, 'dropout': 0.5, 'batch_size': 4},
        {'n_passes': 12, 'learn_rate': 1e-6, 'dropout': 0.6, 'batch_size': 4},
        {'n_passes': 10, 'learn_rate': 5e-6, 'dropout': 0.7, 'batch_size': 4},
        
        # Very long training with tiny steps
        {'n_passes': 50, 'learn_rate': 1e-9, 'dropout': 0.2, 'batch_size': 2},
        {'n_passes': 35, 'learn_rate': 5e-9, 'dropout': 0.3, 'batch_size': 2},
        
        # Balanced approaches
        {'n_passes': 20, 'learn_rate': 1e-7, 'dropout': 0.4, 'batch_size': 4},  # baseline
        {'n_passes': 25, 'learn_rate': 7e-8, 'dropout': 0.35, 'batch_size': 4},
        {'n_passes': 30, 'learn_rate': 3e-8, 'dropout': 0.3, 'batch_size': 4},
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