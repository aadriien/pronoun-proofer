###############################################################################
##  `evaluate_model.py`                                                      ##
##                                                                           ##
##  Purpose: Model evaluation & scoring utilities for coreference model      ##
###############################################################################


import numpy as np
from typing import List, Dict, Tuple, Any
import spacy


class CoreferenceEvaluator:
    def __init__(self):
        self.metrics = {}
    
    def evaluate_model(self, nlp, training_data: List[Dict], total_loss: float = 0.0, 
                      examples_processed: int = 0, sample_size: int = 20) -> float:
        """
        Comprehensive model evaluation with multiple metrics
        
        Args:
            nlp: SpaCy model
            training_data: List of training examples
            total_loss: Training loss for this evaluation
            examples_processed: Number of examples processed during training
            sample_size: Number of examples to evaluate (for speed)
            
        Returns:
            Composite score (higher is better)
        """
        # Sample data for evaluation speed
        eval_data = training_data[:sample_size] if len(training_data) > sample_size else training_data
        
        # Calculate individual metrics
        cluster_detection_rate = self._calculate_cluster_detection_rate(nlp, eval_data)
        cluster_accuracy = self._calculate_cluster_accuracy(nlp, eval_data)
        precision, recall, f1 = self._calculate_precision_recall_f1(nlp, eval_data)
        loss_score = self._calculate_loss_score(total_loss, examples_processed)
        
        # Store metrics for analysis
        self.metrics = {
            'cluster_detection_rate': cluster_detection_rate,
            'cluster_accuracy': cluster_accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'loss_score': loss_score,
            'total_loss': total_loss,
            'examples_processed': examples_processed
        }
        
        # Composite score with weights
        composite_score = (
            0.3 * cluster_detection_rate +
            0.3 * cluster_accuracy +
            0.2 * f1 +
            0.2 * loss_score
        )
        
        return composite_score
    
    def _calculate_cluster_detection_rate(self, nlp, eval_data: List[Dict]) -> float:
        """Calculate percentage of examples where clusters are detected"""
        if not eval_data:
            return 0.0
        
        found_clusters = 0
        for example_data in eval_data:
            text = example_data["text"]
            doc = nlp(text)
            
            if doc.spans and any(len(spans) > 0 for spans in doc.spans.values()):
                found_clusters += 1
        
        return found_clusters / len(eval_data)
    
    def _calculate_cluster_accuracy(self, nlp, eval_data: List[Dict]) -> float:
        """Calculate accuracy of cluster count predictions"""
        if not eval_data:
            return 0.0
        
        total_accuracy = 0.0
        for example_data in eval_data:
            text = example_data["text"]
            expected_clusters = len(example_data["clusters"])
            
            doc = nlp(text)
            detected_clusters = len(doc.spans) if doc.spans else 0
            
            # Accuracy based on how close the cluster count is to expected
            if expected_clusters == 0:
                accuracy = 1.0 if detected_clusters == 0 else 0.0
            else:
                accuracy = max(0.0, 1.0 - abs(detected_clusters - expected_clusters) / expected_clusters)
            
            total_accuracy += accuracy
        
        return total_accuracy / len(eval_data)
    
    def _calculate_precision_recall_f1(self, nlp, eval_data: List[Dict]) -> Tuple[float, float, float]:
        """Calculate precision, recall, and F1 for mention detection"""
        if not eval_data:
            return 0.0, 0.0, 0.0
        
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for example_data in eval_data:
            text = example_data["text"]
            expected_mentions = set()
            
            # Extract expected mentions from clusters
            for cluster in example_data["clusters"]:
                for mention in cluster:
                    expected_mentions.add(mention.lower().strip())
            
            # Get predicted mentions
            doc = nlp(text)
            predicted_mentions = set()
            
            if doc.spans:
                for span_key, spans in doc.spans.items():
                    for span in spans:
                        predicted_mentions.add(span.text.lower().strip())
            
            # Calculate TP, FP, FN
            true_positives += len(expected_mentions & predicted_mentions)
            false_positives += len(predicted_mentions - expected_mentions)
            false_negatives += len(expected_mentions - predicted_mentions)
        
        # Calculate precision, recall, F1
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return precision, recall, f1
    
    def _calculate_loss_score(self, total_loss: float, examples_processed: int) -> float:
        """Convert loss to a score (higher is better)"""
        if examples_processed == 0:
            return 0.0
        
        avg_loss = total_loss / examples_processed
        # Convert loss to score: lower loss = higher score
        loss_score = 1.0 / (1.0 + avg_loss)
        return loss_score
    
    def get_detailed_metrics(self) -> Dict[str, float]:
        """Return detailed metrics from last evaluation"""
        return self.metrics.copy()
    
    def print_evaluation_summary(self, verbose: bool = True):
        """Print a summary of the evaluation results"""
        if not self.metrics:
            print("No evaluation metrics available")
            return
        
        if verbose:
            print("\nDetailed Evaluation Metrics:")
            print("-" * 40)
            print(f"Cluster Detection Rate: {self.metrics['cluster_detection_rate']:.3f}")
            print(f"Cluster Accuracy:       {self.metrics['cluster_accuracy']:.3f}")
            print(f"Mention Precision:      {self.metrics['precision']:.3f}")
            print(f"Mention Recall:         {self.metrics['recall']:.3f}")
            print(f"Mention F1 Score:       {self.metrics['f1_score']:.3f}")
            print(f"Loss Score:             {self.metrics['loss_score']:.3f}")
            
            if self.metrics['examples_processed'] > 0:
                avg_loss = self.metrics['total_loss'] / self.metrics['examples_processed']
                print(f"Average Loss:           {avg_loss:.3f}")
        else:
            # Compact summary
            print(f"Detection: {self.metrics['cluster_detection_rate']:.3f}, "
                  f"Accuracy: {self.metrics['cluster_accuracy']:.3f}, "
                  f"F1: {self.metrics['f1_score']:.3f}")


class ModelComparator:
    def __init__(self):
        self.evaluator = CoreferenceEvaluator()
        self.comparison_results = []
    
    def compare_models(self, models: List[Tuple[Any, str]], test_data: List[Dict]) -> Dict:
        """
        Compare multiple models on the same test data
        
        Args:
            models: List of (model, model_name) tuples
            test_data: Test data for evaluation
            
        Returns:
            Dictionary with comparison results
        """
        results = {}
        
        print(f"\nComparing {len(models)} models on {len(test_data)} test examples...")
        
        for model, model_name in models:
            print(f"\nEvaluating {model_name}...")
            score = self.evaluator.evaluate_model(model, test_data)
            metrics = self.evaluator.get_detailed_metrics()
            
            results[model_name] = {
                'composite_score': score,
                'metrics': metrics
            }
            
            print(f"  Composite Score: {score:.4f}")
        
        # Find best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['composite_score'])
        results['best_model'] = best_model_name
        
        return results
    
    def print_comparison_summary(self, comparison_results: Dict):
        """Print a formatted comparison summary"""
        if not comparison_results:
            print("No comparison results available")
            return
        
        print(f"\n{'='*60}")
        print("MODEL COMPARISON SUMMARY")
        print(f"{'='*60}")
        
        # Sort models by composite score
        sorted_models = sorted(
            [(k, v) for k, v in comparison_results.items() if k != 'best_model'],
            key=lambda x: x[1]['composite_score'],
            reverse=True
        )
        
        print(f"{'Rank':<4} {'Model Name':<20} {'Score':<8} {'Detection':<9} {'Accuracy':<9} {'F1':<8}")
        print("-" * 60)
        
        for rank, (model_name, results) in enumerate(sorted_models, 1):
            score = results['composite_score']
            detection = results['metrics']['cluster_detection_rate']
            accuracy = results['metrics']['cluster_accuracy']
            f1 = results['metrics']['f1_score']
            
            marker = "🏆" if model_name == comparison_results['best_model'] else "  "
            print(f"{marker}{rank:<2} {model_name:<20} {score:<8.4f} {detection:<9.3f} {accuracy:<9.3f} {f1:<8.3f}")
        
        print(f"\nBest Model: {comparison_results['best_model']}")


def quick_evaluate(nlp, test_data: List[Dict], sample_size: int = 50) -> Dict:
    """
    Quick evaluation function for standalone use
    
    Args:
        nlp: SpaCy model to evaluate
        test_data: Test data
        sample_size: Number of examples to test
        
    Returns:
        Dictionary with evaluation results
    """
    evaluator = CoreferenceEvaluator()
    score = evaluator.evaluate_model(nlp, test_data, sample_size=sample_size)
    metrics = evaluator.get_detailed_metrics()
    
    return {
        'composite_score': score,
        'metrics': metrics,
        'evaluator': evaluator
    }


def evaluate_on_sample_text(nlp, sample_texts: List[str]) -> None:
    """
    Test model on sample texts and print results
    
    Args:
        nlp: SpaCy model
        sample_texts: List of text strings to test
    """
    print("\nTesting model on sample texts:")
    print("-" * 50)
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\nExample {i}: '{text}'")
        
        doc = nlp(text)
        if doc.spans:
            print("Detected clusters:")
            for span_key, spans in doc.spans.items():
                mentions = [span.text for span in spans]
                print(f"  {span_key}: {mentions}")
        else:
            print("  No clusters detected")


# Example usage and testing functions
if __name__ == "__main__":
    from model_utils import load_training_data, load_base_model, THEY_THEM_DATA
    
    # Load test data and model
    test_data = load_training_data(json_file=THEY_THEM_DATA)[:10]  # Small sample
    nlp = load_base_model()
    
    if nlp and test_data:
        print("Testing evaluation system...")
        
        # Quick evaluation
        results = quick_evaluate(nlp, test_data)
        print(f"Composite Score: {results['composite_score']:.4f}")
        
        # Print detailed metrics
        evaluator = results['evaluator']
        evaluator.print_evaluation_summary()
        
        # Test on sample texts
        sample_texts = [
            "Alex said they would come to the meeting.",
            "The cat sat on its favorite cushion.",
            "Jordan loves their new job because it gives them flexibility."
        ]
        evaluate_on_sample_text(nlp, sample_texts)