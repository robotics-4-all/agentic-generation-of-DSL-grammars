# Phase 1 Few-Shot Grammar Demonstrations

This directory contains the complete TextX grammars supplied as gold-standard
few-shot demonstrations during Phase 1 of the reported experiments. These files
were reference examples for grammar construction; they were not generated
grammar results or Experiment 2 manual baselines.

## Experiment Mapping

| Experiment | Target grammar(s) generated | Few-shot grammar demonstrations |
| --- | --- | --- |
| Experiment 1 | SmAuto smart-home automation grammars | `goaldsl.tx`, `dflow_experiment1.tx` |
| Experiment 2 | CodinTxt and DFlow grammars | `goaldsl.tx`, `smauto_experiment2.tx` |

GoalDSL was retained as a structurally rich, domain-distinct TextX example in
both experiments. DFlow was used as the second demonstration in Experiment 1.
For Experiment 2, DFlow was an evaluation target, so it was replaced by SmAuto
as the second demonstration. This prevented the target DFlow grammar from being
exposed to the LLM during generation.

## Selection Criteria

The examples were selected to expose the LLM to complete, non-trivial TextX
grammars containing constructs relevant to the methodology, including
polymorphic alternatives, nested composition, cross-references, scoping,
explicit root organization, and realistic multi-rule structures.

The official TextX language definition was supplied separately as a syntax
reference and is not counted as a third few-shot grammar.

## Provenance

- `goaldsl.tx`: extracted verbatim from the GoalDSL grammar embedded in the
  archived Experiment 1 grammar-generation prompt.
- `dflow_experiment1.tx`: the complete DFlow grammar used as the second
  Experiment 1 demonstration.
- `smauto_experiment2.tx`: the complete SmAuto one-file grammar used as the
  second Experiment 2 demonstration.

