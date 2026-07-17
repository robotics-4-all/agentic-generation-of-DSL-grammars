import os
from datetime import datetime
from textx import metamodel_from_str, metamodel_from_file
from grammar_analysis import TextXGrammarAnalyzer
import grammar_analysis
import json


def grammar_validator(grammar_path: str) -> bool:
    """Validates if the grammar text is a valid textX grammar by attempting to create a metamodel from the file."""
    try:
        # Try to create a metamodel directly from the grammar file
        # If the grammar is syntactically valid, this will succeed
        metamodel_from_file(grammar_path)
        
        return True
    except Exception as e:
        print(f"Grammar validation failed: {e}")
        return False


def is_valid_analysis_results(analysis_results):
    """Check if grammar analysis results are valid (don't contain errors)"""
    # Check if results is a dictionary and doesn't contain an "error" key
    if not isinstance(analysis_results, dict):
        return False
    
    # Check for explicit error key
    if "error" in analysis_results:
        return False
    
    # Additional checks can be added here if needed
    # For example, check if required metrics are present
    required_metrics = ["num_rules", "num_non_terminals", "num_terminals"]
    for metric in required_metrics:
        if metric not in analysis_results:
            return False
    
    return True


def save_valid_grammar(grammar_text: str, timestamp: str = None) -> str:
    """Saves valid grammar to results/validated folder with timestamp.
    
    Args:
        grammar_text: The grammar text to save
        timestamp: Optional timestamp string. If None, generates a new one.
    """
    # Create both results/validated and results/metrics directories if they don't exist
    os.makedirs("results/validated", exist_ok=True)
    os.makedirs("results/metrics", exist_ok=True)
    # os.makedirs("results/validated_with_metrics", exist_ok=True)
    # os.makedirs("results/metrics_gram_metrics", exist_ok=True)
    
    # Use provided timestamp or generate a new one
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"grammar_{timestamp}.tx"
    
    filepath = os.path.join("results", "validated", filename)
    metrics_filepath = os.path.join("results", "metrics", f"metrics_{timestamp}.json")
    # filepath = os.path.join("results", "validated_with_metrics", filename)
    # metrics_filepath = os.path.join("results", "metrics_gram_metrics", f"metrics_{timestamp}.json")
    
    # First, try to analyze the grammar
    analyzer = TextXGrammarAnalyzer()
    try:
        grammar_analysis_results = analyzer.analyze_grammar(grammar_text)
        
        # Check if analysis results are valid
        if not is_valid_analysis_results(grammar_analysis_results):
            print("Grammar analysis failed or produced invalid results. Grammar not saved.")
            return None
        
        # Prepare serializable results
        serializable_results = {}
        for key, metric in grammar_analysis_results.items():
            if hasattr(metric, 'dict'):
                serializable_results[key] = metric.dict()
            else:
                serializable_results[key] = str(metric)
        
        # Save the grammar file only if analysis was successful
        with open(filepath, "w") as file:
            file.write(grammar_text)
        
        # Save the metrics
        with open(metrics_filepath, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"Successfully saved grammar and metrics: {filename}")
        return filepath
        
    except Exception as e:
        print(f"Grammar analysis failed with exception: {e}")
        # Don't save anything if analysis fails
        return None


def validate_and_save_grammar(grammar_text: str) -> bool:
    """
    Complete validation pipeline: validate grammar syntax and quality metrics.
    Returns True if both validations pass and files are saved, False otherwise.
    """
    # Create a temporary file to validate the grammar syntax
    temp_filepath = "temp_grammar_validation.tx"
    
    try:
        # Write grammar to temporary file
        with open(temp_filepath, "w") as temp_file:
            temp_file.write(grammar_text)
        
        # Validate grammar syntax
        if not grammar_validator(temp_filepath):
            print("Grammar syntax validation failed")
            return False
        
        # If syntax validation passes, try to save with quality metrics
        saved_filepath = save_valid_grammar(grammar_text)
        
        # Return True only if grammar was successfully saved (which means metrics were also valid)
        return saved_filepath is not None
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)