# Revision Artifact Repository: Handoff Report

## Purpose

This repository is the supplementary-artifact package for the major revision of *Beyond Syntactic Correctness: Agentic Generation of DSL Grammars Optimized for LLM-Based Model Generation*.

It provides concrete artifacts requested by the reviewers. It is deliberately **not** a source-code or raw-log release. Methodological explanations, validity arguments, statistical analysis, and reviewer responses belong in the revised manuscript and response letter.

## Reviewer-Facing Artifacts Included

### 1. Complete anti-pattern catalog

Location: `supplementary/anti_pattern_catalog.md` and `supplementary/anti_pattern_catalog.json`

Contents: the twelve grammar-level anti-patterns targeted during Phase 2, organized by structural dimension. Each entry includes the problematic construct, preferred rewriting, symptom during LLM-based generation, and rationale.

Paper use: supports the request for concrete anti-pattern examples and makes the Phase 2 structural optimization inspectable.

### 2. Concrete grammar and model-generation examples

Location: `supplementary/reviewer_artifact_examples/`

Contents:

- `grammars/dflow_high_performing_generated_grammar_20251208_181906.tx`: a real methodology-generated DFlow grammar. Under Qwen3 Coder Flash cross-model evaluation, it achieved 94.44% attempt-level and 97.22% prompt-level syntactic success.
- `grammars/experiment1_zero_success_baseline_grammar_20251008_163427.tx`: a real Experiment 1 Condition 1 grammar that is syntactically valid as TextX but achieved 0/60 valid downstream model generations. It is a valid but low-perceivability grammar, not an invalid grammar specification.
- `model_instances/dflow_prompt_003.txt`: a real DFlow evaluation prompt.
- `model_instances/dflow_prompt_003_manual_qwen_invalid_model.json`: a Qwen output generated using the manual DFlow grammar that fails TextX validation.
- `model_instances/dflow_prompt_003_generated_grammar_qwen_valid_model.txt`: a Qwen output for the same prompt using the generated DFlow grammar that validates successfully.
- `README.md`: provenance and recommended manuscript placement for these artifacts.

Paper use: supports the requests for a specific generated grammar, examples of generated models from manual and generated DSLs, and tangible examples accompanying Experiment 2.

### 3. Prompt templates

Location: `prompt_templates/`

Contents: the active templates used for grammar generation, refinement, curriculum/sample-model generation, documentation generation, error guidance, and simple/medium/high model generation.

Paper use: supports the statement that the project releases its prompt material. No runtime logs or API transcripts are included.

### 4. Evaluation prompts and requirements

Locations: `evaluation_prompts/` and `requirement_specifications/`

Contents: the full 157-prompt CodinTxt evaluation set, 180-prompt DFlow evaluation set, and the 8 smart-home, 22 CodinTxt, and 24 DFlow requirement specifications.

Paper use: provides the concrete inputs used to generate and evaluate the grammars reported in both experiments.

### 5. Complete generated grammar corpora

Location: `generated_grammars/`

Contents: all ten CodinTxt and all ten DFlow grammars evaluated in Experiment 2, plus all 700 grammars used in the seven reported Experiment 1 conditions (100 grammars per condition). The unrelated 100-grammar correlation-analysis corpus is not included.

Paper use: lets readers inspect the complete evaluated grammar populations rather than only selected examples.

### 6. Manual Experiment 2 grammars

Location: `manual_grammars/`

Contents:

- `codintxt_manual.tx`
- `dflow_manual.tx`

Paper use: provides the actual manual baselines behind the Experiment 2 comparison and lets readers inspect the grammar associated with the manual-versus-generated DFlow model example.

### 7. Repository-level guide

Location: `README.md`

Contents: a concise description of the manuscript, repository scope, and an artifact map from paper topics to files.

### 8. Focused validation and statistical scripts

Location: `validation_scripts/`

Contents: the grammar validator, model validator, Experiment 1 statistical-test script, Experiment 2 statistical-test script, and their Python dependency list.

Paper use: supports the stated availability of validation scripts without releasing the broader grammar-generation pipeline.

## Explicitly Not Included

The repository does not include the broader grammar-generation source code, LLM client integrations, orchestration code, raw execution logs, API/cache records, or model-attempt corpora. It includes only the focused validation and statistical scripts described above.

## Revision Wording Notes

- Do not describe the Experiment 1 zero-success grammar as an invalid grammar. It compiles successfully; its point is that syntactic grammar validity does not guarantee valid LLM-generated models.
- Do not present the DFlow manual-versus-generated model pair as a standalone statistical proof. It is an illustrative example; the aggregate experiment results and formal statistics provide the evidence.
- The anti-pattern JSON is a released machine-readable representation of the catalog. Avoid saying that this specific JSON file was directly consumed by the original optimizer unless the manuscript can substantiate that implementation detail.
