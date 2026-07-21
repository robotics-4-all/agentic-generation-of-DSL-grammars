# Agentic Generation of DSL Grammars: Supplementary Artifacts

This repository accompanies the manuscript *Beyond Syntactic Correctness: Agentic Generation of DSL Grammars Optimized for LLM-Based Model Generation*.

It provides the concrete supplementary artifacts referenced in the revised manuscript:

- `supplementary/anti_pattern_catalog.md` and `supplementary/anti_pattern_catalog.json`: the complete catalog of twelve grammar-level anti-patterns targeted during structural optimization.
- `supplementary/reviewer_artifact_examples/`: real grammar and model-generation examples used to illustrate the reported experiments.
- `prompt_templates/`: the active prompt templates used by the four-phase methodology.
- `few_shot_grammars/`: the complete GoalDSL, DFlow, and SmAuto grammars used as Phase 1 demonstrations, with the experiment-specific mapping documented in that directory.
- `evaluation_prompts/`: the 157 CodinTxt and 180 DFlow natural-language evaluation prompts.
- `requirement_specifications/`: the 8 smart-home, 22 CodinTxt, and 24 DFlow functional requirements.
- `manual_grammars/`: the manually crafted CodinTxt and DFlow TextX grammars used as Experiment 2 baselines.
- `generated_grammars/`: all 20 Experiment 2 grammars and all 700 grammars from the seven reported Experiment 1 conditions.
- `validation_scripts/`: the focused grammar/model validation and statistical-test scripts used for the evaluation.

The repository intentionally contains supplementary artifacts and focused validation scripts, not the broader grammar-generation pipeline or raw execution logs. Methodological rationale, experimental design, and limitations are described in the manuscript and its response to reviewers.

## Artifact Map

| Paper topic | Repository artifact |
| --- | --- |
| Phase 1--4 prompt design | `prompt_templates/` |
| Phase 1 gold-standard few-shot examples | `few_shot_grammars/` |
| Experiment 1 and 2 requirements | `requirement_specifications/` |
| Experiment 2 natural-language evaluation prompts | `evaluation_prompts/` |
| Phase 2 anti-pattern catalog | `supplementary/anti_pattern_catalog.*` |
| Experiment 2 manual baselines | `manual_grammars/` |
| Experiment 1 and 2 generated grammars | `generated_grammars/` |
| Parser validation and statistical testing | `validation_scripts/` |
| Concrete generated grammar examples | `supplementary/reviewer_artifact_examples/grammars/` |
| Manual-versus-generated model instance | `supplementary/reviewer_artifact_examples/model_instances/` |

See `supplementary/reviewer_artifact_examples/README.md` for the provenance and interpretation of the concrete grammar and model artifacts.
