#!/usr/bin/env python3
"""
Model Validation Script

This script validates generated models against their corresponding grammar using textX.
Takes a timestamp and complexity level as arguments and validates all models (both valid and invalid).

Usage:
    python model_validator.py <timestamp> <complexity>

Example:
    python model_validator.py 20250901_152948 medium
"""

import sys
import argparse
from pathlib import Path
import os
from textx import metamodel_from_file
from textx.exceptions import TextXSyntaxError, TextXSemanticError


class ModelValidator:
    def __init__(self, results_path="results"):
        """
        Initialize the model validator

        Args:
            results_path (str): Path to the results folder
        """
        self.results_path = Path(results_path)
        self.validated_path = self.results_path / "validated"
        self.model_text_path = self.results_path / "model-text"

    def find_grammar_file(self, timestamp):
        """
        Find the grammar file for the given timestamp

        Args:
            timestamp (str): Grammar timestamp (e.g., "20250901_152948")

        Returns:
            Path: Path to the grammar file or None if not found
        """
        grammar_file = self.validated_path / f"grammar_{timestamp}.tx"

        if not grammar_file.exists():
            print(f"ERROR: Grammar file not found: {grammar_file}")
            return None

        return grammar_file

    def find_all_models(self, timestamp, complexity):
        """
        Find all model files for the given timestamp and complexity (both valid and invalid)

        Args:
            timestamp (str): Model timestamp
            complexity (str): Complexity level (simple, medium, high)

        Returns:
            list: List of tuples (model_path, expected_status) for all model files
        """
        model_dir = self.model_text_path / timestamp / complexity

        if not model_dir.exists():
            print(f"ERROR: Model directory not found: {model_dir}")
            return []

        # Find all model files (both valid and invalid)
        all_models = []

        # Pattern: model_XX_valid.txt or model_XX_invalid.txt
        for model_file in model_dir.glob("model_*_*.txt"):
            # Extract the expected status from filename
            parts = model_file.stem.split("_")
            if len(parts) >= 3:
                expected_status = parts[2]  # 'valid' or 'invalid'
                all_models.append((model_file, expected_status))

        return sorted(all_models, key=lambda x: x[0].name)

    def validate_grammar_syntax(self, grammar_file):
        """
        Validate the grammar file syntax using both textX methods

        Args:
            grammar_file (Path): Path to the grammar file

        Returns:
            dict: Validation results for both methods
        """
        results = {
            "from_file": {"success": False, "error": None},
            "from_string": {"success": False, "error": None},
            "grammar_content": None,
        }

        print("GRAMMAR VALIDATION:")
        print("-" * 30)

        try:
            # Read the grammar content
            with open(grammar_file, "r", encoding="utf-8") as f:
                grammar_content = f.read()
            results["grammar_content"] = grammar_content

        except Exception as e:
            error_msg = f"Grammar file reading error: {str(e)}"
            results["from_file"]["error"] = error_msg
            results["from_string"]["error"] = error_msg
            print(f"✗ Failed to read grammar file: {error_msg}")
            return results

        # Method 1: metamodel_from_file (grammar validation)
        print(f"→ Testing grammar with metamodel_from_file()...")
        try:
            metamodel_file = metamodel_from_file(str(grammar_file))
            results["from_file"]["success"] = True
            print(f"  ✓ metamodel_from_file: Grammar is VALID")

        except TextXSyntaxError as e:
            error_msg = f"Grammar Syntax Error: {str(e)}"
            results["from_file"]["error"] = error_msg
            print(f"  ✗ metamodel_from_file: {error_msg}")

        except TextXSemanticError as e:
            error_msg = f"Grammar Semantic Error: {str(e)}"
            results["from_file"]["error"] = error_msg
            print(f"  ✗ metamodel_from_file: {error_msg}")

        except Exception as e:
            error_msg = f"Grammar Unexpected Error: {str(e)}"
            results["from_file"]["error"] = error_msg
            print(f"  ✗ metamodel_from_file: {error_msg}")

        # Method 2: metamodel_from_str (grammar validation)
        print(f"→ Testing grammar with metamodel_from_str()...")
        try:
            from textx import metamodel_from_str

            metamodel_str = metamodel_from_str(grammar_content)
            results["from_string"]["success"] = True
            print(f"  ✓ metamodel_from_str: Grammar is VALID")

        except TextXSyntaxError as e:
            error_msg = f"Grammar Syntax Error: {str(e)}"
            results["from_string"]["error"] = error_msg
            print(f"  ✗ metamodel_from_str: {error_msg}")

        except TextXSemanticError as e:
            error_msg = f"Grammar Semantic Error: {str(e)}"
            results["from_string"]["error"] = error_msg
            print(f"  ✗ metamodel_from_str: {error_msg}")

        except Exception as e:
            error_msg = f"Grammar Unexpected Error: {str(e)}"
            results["from_string"]["error"] = error_msg
            print(f"  ✗ metamodel_from_str: {error_msg}")

        # Summary for grammar validation
        if results["from_file"]["success"] and results["from_string"]["success"]:
            print(
                f"→ Grammar Result: ✓ BOTH METHODS - Grammar is syntactically correct"
            )
        elif results["from_file"]["success"] or results["from_string"]["success"]:
            print(f"→ Grammar Result: ⚠ PARTIAL - Only one method succeeded")
        else:
            print(f"→ Grammar Result: ✗ BOTH FAILED - Grammar has syntax errors")

        print()
        return results

    def validate_model_with_grammar(self, grammar_file, model_file):
        """
        Validate a model file against a grammar using textX (both from file and from string)

        Args:
            grammar_file (Path): Path to the grammar file
            model_file (Path): Path to the model file

        Returns:
            dict: Validation results for both methods
        """
        results = {
            "from_file": {"success": False, "error": None},
            "from_string": {"success": False, "error": None},
            "model_content": None,
        }

        try:
            # Read the model content
            with open(model_file, "r", encoding="utf-8") as f:
                model_content = f.read()
            results["model_content"] = model_content

            # Read the grammar content
            with open(grammar_file, "r", encoding="utf-8") as f:
                grammar_content = f.read()

        except Exception as e:
            error_msg = f"File reading error: {str(e)}"
            results["from_file"]["error"] = error_msg
            results["from_string"]["error"] = error_msg
            return results

        # Method 1: metamodel_from_file
        print(f"    → Testing metamodel_from_file()...")
        try:
            metamodel_file = metamodel_from_file(str(grammar_file))
            model_file_obj = metamodel_file.model_from_file(str(model_file))
            results["from_file"]["success"] = True
            print(f"      ✓ metamodel_from_file: SUCCESS")

        except TextXSyntaxError as e:
            error_msg = f"Syntax Error: {str(e)}"
            results["from_file"]["error"] = error_msg
            print(f"      ✗ metamodel_from_file: {error_msg}")

        except TextXSemanticError as e:
            error_msg = f"Semantic Error: {str(e)}"
            results["from_file"]["error"] = error_msg
            print(f"      ✗ metamodel_from_file: {error_msg}")

        except Exception as e:
            error_msg = f"Unexpected Error: {str(e)}"
            results["from_file"]["error"] = error_msg
            print(f"      ✗ metamodel_from_file: {error_msg}")

        # Method 2: metamodel_from_str
        print(f"    → Testing metamodel_from_str()...")
        try:
            from textx import metamodel_from_str

            metamodel_str = metamodel_from_str(grammar_content)
            model_str_obj = metamodel_str.model_from_str(model_content)
            results["from_string"]["success"] = True
            print(f"      ✓ metamodel_from_str: SUCCESS")

        except TextXSyntaxError as e:
            error_msg = f"Syntax Error: {str(e)}"
            results["from_string"]["error"] = error_msg
            print(f"      ✗ metamodel_from_str: {error_msg}")

        except TextXSemanticError as e:
            error_msg = f"Semantic Error: {str(e)}"
            results["from_string"]["error"] = error_msg
            print(f"      ✗ metamodel_from_str: {error_msg}")

        except Exception as e:
            error_msg = f"Unexpected Error: {str(e)}"
            results["from_string"]["error"] = error_msg
            print(f"      ✗ metamodel_from_str: {error_msg}")

        return results

    def validate_models(self, timestamp, complexity):
        """
        Validate all models for the given timestamp and complexity

        Args:
            timestamp (str): Grammar/model timestamp
            complexity (str): Complexity level
        """
        print(f"Model Validation for Timestamp: {timestamp}, Complexity: {complexity}")
        print("=" * 70)

        # Find grammar file
        grammar_file = self.find_grammar_file(timestamp)
        if not grammar_file:
            return

        print(f"Grammar file: {grammar_file}")
        print()

        # Validate grammar syntax first
        grammar_results = self.validate_grammar_syntax(grammar_file)

        # If grammar validation failed completely, don't proceed with model validation
        if (
            not grammar_results["from_file"]["success"]
            and not grammar_results["from_string"]["success"]
        ):
            print(
                "❌ STOPPING: Grammar validation failed with both methods. Cannot validate models."
            )
            return {"grammar_invalid": True, "grammar_results": grammar_results}

        # Find all models (both valid and invalid)
        all_models = self.find_all_models(timestamp, complexity)
        if not all_models:
            print(f"No models found for {timestamp}/{complexity}")
            return {"no_models": True, "grammar_results": grammar_results}

        print(f"Found {len(all_models)} models to validate")
        print()

        # Validate each model
        validation_results = {
            "grammar_results": grammar_results,
            "total_models": len(all_models),
            "from_file": {"valid": 0, "invalid": 0},
            "from_string": {"valid": 0, "invalid": 0},
            "both_methods_agree": 0,
            "methods_disagree": 0,
            "expected_valid_correct_file": 0,
            "expected_valid_wrong_file": 0,
            "expected_invalid_correct_file": 0,
            "expected_invalid_wrong_file": 0,
            "expected_valid_correct_string": 0,
            "expected_valid_wrong_string": 0,
            "expected_invalid_correct_string": 0,
            "expected_invalid_wrong_string": 0,
            "disagreements": [],
            "failures": [],
        }

        for i, (model_file, expected_status) in enumerate(all_models, 1):
            model_name = model_file.name
            print(
                f"[{i}/{len(all_models)}] Validating {model_name} (expected: {expected_status})..."
            )

            results = self.validate_model_with_grammar(grammar_file, model_file)

            file_success = results["from_file"]["success"]
            string_success = results["from_string"]["success"]

            # Update method counters
            if file_success:
                validation_results["from_file"]["valid"] += 1
            else:
                validation_results["from_file"]["invalid"] += 1

            if string_success:
                validation_results["from_string"]["valid"] += 1
            else:
                validation_results["from_string"]["invalid"] += 1

            # Check if methods agree
            if file_success == string_success:
                validation_results["both_methods_agree"] += 1
                agreement_status = "AGREE"
            else:
                validation_results["methods_disagree"] += 1
                agreement_status = "DISAGREE"
                validation_results["disagreements"].append(
                    {
                        "file": model_name,
                        "expected": expected_status,
                        "from_file": file_success,
                        "from_string": string_success,
                        "file_error": results["from_file"]["error"],
                        "string_error": results["from_string"]["error"],
                    }
                )

            # Check expectation accuracy for both methods
            if expected_status == "valid":
                if file_success:
                    validation_results["expected_valid_correct_file"] += 1
                else:
                    validation_results["expected_valid_wrong_file"] += 1

                if string_success:
                    validation_results["expected_valid_correct_string"] += 1
                else:
                    validation_results["expected_valid_wrong_string"] += 1
            else:  # expected_status == 'invalid'
                if not file_success:
                    validation_results["expected_invalid_correct_file"] += 1
                else:
                    validation_results["expected_invalid_wrong_file"] += 1

                if not string_success:
                    validation_results["expected_invalid_correct_string"] += 1
                else:
                    validation_results["expected_invalid_wrong_string"] += 1

            # Log the final result for this model
            print(f"    → Final Result: Methods {agreement_status}")
            if file_success and string_success:
                print(f"      ✓ BOTH VALID - Model is syntactically correct")
            elif not file_success and not string_success:
                print(f"      ✗ BOTH INVALID - Model has syntax errors")
            else:
                print(
                    f"      ⚠ MIXED RESULTS - File: {'valid' if file_success else 'invalid'}, String: {'valid' if string_success else 'invalid'}"
                )

            # Check expectation match
            expected_correct_file = (expected_status == "valid" and file_success) or (
                expected_status == "invalid" and not file_success
            )
            expected_correct_string = (
                expected_status == "valid" and string_success
            ) or (expected_status == "invalid" and not string_success)

            if expected_correct_file and expected_correct_string:
                print(
                    f"      ✓ EXPECTATION: Both methods match expected status ({expected_status})"
                )
            elif expected_correct_file or expected_correct_string:
                print(
                    f"      ⚠ EXPECTATION: Only one method matches expected status ({expected_status})"
                )
            else:
                print(
                    f"      ✗ EXPECTATION: Neither method matches expected status ({expected_status})"
                )

            print()

        # Print comprehensive summary
        print("VALIDATION SUMMARY")
        print("=" * 50)

        # Grammar validation summary
        print("GRAMMAR VALIDATION:")
        grammar_file_ok = validation_results["grammar_results"]["from_file"]["success"]
        grammar_string_ok = validation_results["grammar_results"]["from_string"][
            "success"
        ]

        if grammar_file_ok and grammar_string_ok:
            print("  ✓ Grammar is valid with both methods")
        elif grammar_file_ok or grammar_string_ok:
            print("  ⚠ Grammar is valid with only one method")
            if not grammar_file_ok:
                print(
                    f"    - File method error: {validation_results['grammar_results']['from_file']['error']}"
                )
            if not grammar_string_ok:
                print(
                    f"    - String method error: {validation_results['grammar_results']['from_string']['error']}"
                )
        else:
            print("  ✗ Grammar validation failed with both methods")
            print(
                f"    - File method error: {validation_results['grammar_results']['from_file']['error']}"
            )
            print(
                f"    - String method error: {validation_results['grammar_results']['from_string']['error']}"
            )

        print()
        print(f"Total models validated: {validation_results['total_models']}")
        print()

        print("METHOD RESULTS:")
        print(
            f"  metamodel_from_file   - Valid: {validation_results['from_file']['valid']}, Invalid: {validation_results['from_file']['invalid']}"
        )
        print(
            f"  metamodel_from_str    - Valid: {validation_results['from_string']['valid']}, Invalid: {validation_results['from_string']['invalid']}"
        )
        print()

        print("METHOD AGREEMENT:")
        print(f"  Both methods agree: {validation_results['both_methods_agree']}")
        print(f"  Methods disagree: {validation_results['methods_disagree']}")
        agreement_rate = (
            validation_results["both_methods_agree"]
            / validation_results["total_models"]
            * 100
            if validation_results["total_models"] > 0
            else 0
        )
        print(f"  Agreement rate: {agreement_rate:.1f}%")
        print()

        print("EXPECTATION ACCURACY:")
        print("  From File Method:")
        print(
            f"    Expected valid & correct: {validation_results['expected_valid_correct_file']}"
        )
        print(
            f"    Expected valid & wrong: {validation_results['expected_valid_wrong_file']}"
        )
        print(
            f"    Expected invalid & correct: {validation_results['expected_invalid_correct_file']}"
        )
        print(
            f"    Expected invalid & wrong: {validation_results['expected_invalid_wrong_file']}"
        )

        file_accuracy = (
            (
                validation_results["expected_valid_correct_file"]
                + validation_results["expected_invalid_correct_file"]
            )
            / validation_results["total_models"]
            * 100
            if validation_results["total_models"] > 0
            else 0
        )
        print(f"    File method accuracy: {file_accuracy:.1f}%")

        print("  From String Method:")
        print(
            f"    Expected valid & correct: {validation_results['expected_valid_correct_string']}"
        )
        print(
            f"    Expected valid & wrong: {validation_results['expected_valid_wrong_string']}"
        )
        print(
            f"    Expected invalid & correct: {validation_results['expected_invalid_correct_string']}"
        )
        print(
            f"    Expected invalid & wrong: {validation_results['expected_invalid_wrong_string']}"
        )

        string_accuracy = (
            (
                validation_results["expected_valid_correct_string"]
                + validation_results["expected_invalid_correct_string"]
            )
            / validation_results["total_models"]
            * 100
            if validation_results["total_models"] > 0
            else 0
        )
        print(f"    String method accuracy: {string_accuracy:.1f}%")

        if validation_results["disagreements"]:
            print(
                f"\nMETHOD DISAGREEMENTS ({len(validation_results['disagreements'])}):"
            )
            for disagreement in validation_results["disagreements"]:
                print(
                    f"  • {disagreement['file']} (expected: {disagreement['expected']}):"
                )
                print(
                    f"    - From file: {'valid' if disagreement['from_file'] else 'invalid'}"
                    + (
                        f" - {disagreement['file_error']}"
                        if disagreement["file_error"]
                        else ""
                    )
                )
                print(
                    f"    - From string: {'valid' if disagreement['from_string'] else 'invalid'}"
                    + (
                        f" - {disagreement['string_error']}"
                        if disagreement["string_error"]
                        else ""
                    )
                )

        return validation_results

    def list_available_data(self):
        """List available timestamps and complexity levels"""
        print("Available data:")
        print("=" * 30)

        if not self.model_text_path.exists():
            print("No model-text directory found")
            return

        timestamps = []
        for timestamp_dir in self.model_text_path.iterdir():
            if timestamp_dir.is_dir():
                # Check if corresponding grammar exists
                grammar_file = self.validated_path / f"grammar_{timestamp_dir.name}.tx"

                complexities = []
                for complexity_dir in timestamp_dir.iterdir():
                    if complexity_dir.is_dir() and complexity_dir.name in [
                        "simple",
                        "medium",
                        "high",
                    ]:
                        # Count valid and invalid models
                        valid_count = len(
                            list(complexity_dir.glob("model_*_valid.txt"))
                        )
                        invalid_count = len(
                            list(complexity_dir.glob("model_*_invalid.txt"))
                        )
                        total_count = valid_count + invalid_count

                        if total_count > 0:
                            complexities.append(
                                f"{complexity_dir.name}({valid_count}v/{invalid_count}i)"
                            )

                if complexities:
                    status = "✓" if grammar_file.exists() else "✗ (no grammar)"
                    timestamps.append(
                        {
                            "timestamp": timestamp_dir.name,
                            "complexities": complexities,
                            "status": status,
                        }
                    )

        if not timestamps:
            print("No valid data found")
            return

        timestamps.sort(key=lambda x: x["timestamp"])

        for data in timestamps:
            print(
                f"{data['status']} {data['timestamp']}: {', '.join(data['complexities'])}"
            )

        print(f"\nTotal timestamps: {len(timestamps)}")
        print("Format: complexity(valid_count v / invalid_count i)")


def main():
    parser = argparse.ArgumentParser(
        description="Validate generated models against their grammar using textX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python model_validator.py 20250901_152948 medium
  python model_validator.py 20250902_141030 simple
  python model_validator.py --list
        """,
    )

    parser.add_argument(
        "timestamp", nargs="?", help="Grammar timestamp (e.g., 20250901_152948)"
    )
    parser.add_argument(
        "complexity",
        nargs="?",
        choices=["simple", "medium", "high"],
        help="Complexity level",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available timestamps and complexity levels",
    )
    parser.add_argument(
        "--results-path",
        default="results",
        help="Path to results directory (default: results)",
    )

    args = parser.parse_args()

    validator = ModelValidator(results_path=args.results_path)

    if args.list:
        validator.list_available_data()
        return

    if not args.timestamp or not args.complexity:
        print("ERROR: Both timestamp and complexity are required (unless using --list)")
        print("Use --help for usage information")
        sys.exit(1)

    # Validate the models
    try:
        results = validator.validate_models(args.timestamp, args.complexity)

        # Exit with appropriate code based on results
        if (
            results
            and not results.get("grammar_invalid")
            and not results.get("no_models")
        ):
            # Check if there were validation issues
            invalid_count = results.get("from_file", {}).get(
                "invalid", 0
            ) + results.get("from_string", {}).get("invalid", 0)
            if invalid_count == 0:
                sys.exit(0)  # All models valid
            else:
                sys.exit(1)  # Some models invalid
        else:
            sys.exit(1)  # Grammar invalid or no models found

    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
