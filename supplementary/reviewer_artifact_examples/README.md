# Reviewer Artifact Examples

This packet contains concrete artifacts that can be used in the manuscript revision and/or supplementary material to address reviewer requests for examples.

The reviewers asked for:

- examples of valid and non-valid auto-generated grammars;
- a specific example of a generated grammar;
- instances of models created by the LLM from generated and manual DSLs;
- concrete artifacts rather than only abstract descriptions.

The files in this folder are real outputs from the project, not reconstructed examples.

## Folder Contents

```text
reviewer_artifact_examples/
  grammars/
    dflow_high_performing_generated_grammar_20251208_181906.tx
    experiment1_zero_success_baseline_grammar_20251008_163427.tx
  model_instances/
    dflow_prompt_003.txt
    dflow_prompt_003_manual_qwen_invalid_model.json
    dflow_prompt_003_generated_grammar_qwen_valid_model.txt
```

## Artifact 1: High-Performing Generated Grammar

File:

```text
grammars/dflow_high_performing_generated_grammar_20251208_181906.tx
```

Origin:

```text
version_1_results/results-dflow/validated/grammar_20251208_181906.tx
```

Why this artifact was selected:

- It is an actual generated DFlow grammar from Experiment 2.
- It is syntactically valid.
- It is one of the strongest generated DFlow grammars.
- Under the Qwen cross-model rerun it achieved:

```text
Attempt-level success: 94.44%
Prompt-level success:  97.22%
```

Recommended use in the paper:

- Include a representative excerpt in the appendix.
- Link the full file in the reproducibility repository.
- Use it as the concrete example requested by R1/R2: "a specific example of a generated grammar."

## Artifact 2: Syntactically Valid but Zero-Success Baseline Grammar

File:

```text
grammars/experiment1_zero_success_baseline_grammar_20251008_163427.tx
```

Origin:

```text
version_1_results/experiment_results/1)-initial-results-no-refinement/results/validated/grammar_20251008_163427.tx
```

Why this artifact was selected:

- It is a real grammar from Experiment 1, Condition 1.
- It is syntactically valid as a textX grammar.
- It achieved zero downstream model-generation success:

```text
simple: 0/20
medium: 0/20
high: 0/20
overall: 0/60
```

Relevant metric profile:

```text
Rules: 49
Terminals: 197
Choice points: 161
Recursive rules: 8
Maximum rule length: 228
```

Why this is useful:

- It illustrates the central argument of the paper: syntactic grammar validity is not enough.
- A grammar can be parseable and still difficult for LLMs to use for valid model generation.
- It can be discussed alongside the anti-pattern catalog.

Recommended use in the paper:

- Include an excerpt in an appendix as a "valid but low-perceivability" grammar.
- Use it to ground the discussion of failed baseline grammars and anti-patterns.

## Artifact 3: DFlow Prompt Used for Manual-vs-Generated Model Comparison

File:

```text
model_instances/dflow_prompt_003.txt
```

Prompt:

```text
create an assistant which presents the nearest charging stations using /openstreetmaps/get_charging_stations. 
First it collects from the user the latitude the longitude and the radius from the user and then using eservices with host: 'r4a.issel.ee.auth.gr' port: 8080 gets the path: '/openstreetmaps/get_charging_stations'
```

Why this prompt was selected:

- It is a real DFlow prompt from Experiment 2.
- It produces a clear contrast between manual and generated grammar behavior under Qwen.
- The manual grammar output fails validation.
- The generated grammar output validates successfully.

## Artifact 4: Manual DFlow Grammar Output, Invalid

File:

```text
model_instances/dflow_prompt_003_manual_qwen_invalid_model.json
```

Origin:

```text
version_2_results/experiment_2_cross_llm_qwen3_coder_flash/dflow_experiment/manual/prompt_003/model_attempt_1_invalid.json
```

Validation result:

```text
INVALID
```

Validation error:

```text
None:25:29: Expected ',' or 'end' => ' float = 0*.0     use'
```

Excerpt of generated model:

```text
Metadata
    name: "Charging Station Finder"
    description: "Assistant to find nearest charging stations using OpenStreetMap data"
    author: "Assistant Developer"
    email: "developer@assistant.com"
end

entities
    Entity LOCATION_COORDINATES
        "latitude",
        "longitude",
        "radius"
    end
end

gslots
    user_latitude: float = 0.0
    user_longitude: float = 0.0
    user_radius: float = 0.0
end
```

Why this artifact is useful:

- It shows a concrete model instance generated from the manual DFlow grammar.
- The model is plausible but fails syntactic validation.
- It makes the low DFlow manual success rate tangible.

## Artifact 5: Generated DFlow Grammar Output, Valid

File:

```text
model_instances/dflow_prompt_003_generated_grammar_qwen_valid_model.txt
```

Origin:

```text
version_2_results/experiment_2_cross_llm_qwen3_coder_flash/dflow_experiment/grammar_20251208_181906/prompt_003/model_attempt_3_valid.txt
```

Validation result:

```text
VALID
```

Excerpt of generated model:

```text
entities
    Entity latitude_value
        "latitude", "lat", "position north"
    end
    Entity longitude_value
        "longitude", "lng", "position east"
    end
    Entity radius_value
        "radius", "range", "distance"
    end
end

gslots
    user_latitude : float,
    user_longitude : float,
    user_radius : float
end

eservices
    EServiceHTTP charging_station_service
        verb: GET
        host: "r4a.issel.ee.auth.gr"
        port: 8080
        path: "/openstreetmaps/get_charging_stations"
    end
end
```

Why this artifact is useful:

- It shows a concrete model instance generated from a methodology-generated DFlow grammar.
- It validates successfully under the same Qwen model-generation setup.
- It directly illustrates why the generated DFlow grammars outperform the manual DFlow grammar in Experiment 2.

## How to Use These in the Manuscript

Recommended placement:

1. Main text, Experiment 2 results:
   - Add a short "Illustrative Example" subsection.
   - Show the DFlow prompt and a compact manual-vs-generated model comparison.
   - Mention that the full artifacts are available in the supplementary repository.

2. Appendix:
   - Include an excerpt from the high-performing generated DFlow grammar.
   - Include an excerpt from the zero-success baseline grammar.
   - Explain how the zero-success grammar demonstrates that syntactic validity alone is insufficient.

3. Supplementary repository:
   - Include all files in this packet.
   - Include the anti-pattern catalog in both Markdown and JSON.

## Suggested Manuscript Text

```latex
\added{To make the quantitative results more concrete, Appendix~X includes real artifacts from the evaluation: a high-performing generated DFlow grammar, a syntactically valid but zero-success baseline grammar from Experiment~1, and a DFlow prompt for which Qwen generated an invalid model using the manual grammar but a valid model using a generated grammar. These examples illustrate that the measured differences are not only aggregate effects: they correspond to observable differences in the model instances produced from the same natural-language request.}
```

## Important Framing

These artifacts should not be used to claim that generated grammars always outperform manual grammars. The correct claim is more careful:

```text
Generated grammars remain highly LLM-perceivable under cross-model evaluation, and in DFlow several generated grammars substantially outperform the manual baseline.
```

This framing matches the final Qwen results:

```text
CodinTxt generated prompt success: 91.78%
DFlow generated prompt success:    76.39%
DFlow manual prompt success:       37.78%
```
