# Grammar Anti-Pattern Catalog

This catalog summarizes the structural grammar anti-patterns targeted by the methodology. The patterns are derived from the refinement rules used in the project and are written in a form suitable for a paper appendix, reproducibility package, or response to reviewers.

The purpose of the catalog is not only to produce syntactically valid textX grammars, but also to make grammars easier for LLMs to interpret and use for downstream model generation.

## AP1. Ambiguous Choice Ordering

**Problem.** Alternatives with overlapping token patterns are ordered in a way that causes the parser or the LLM to select the wrong construct.

**Typical symptom.**

- Valid-looking models fail because a broader or narrower alternative is matched too early.
- LLMs produce examples that look plausible but are parsed as the wrong rule.

**Before.**

```text
Action:
    IntAction | FloatAction | StringAction
;
```

**After.**

```text
Action:
    FloatAction | IntAction | StringAction
;
```

**Rationale.** When alternatives overlap, the grammar should order them consistently according to textX/parser behavior and the intended recognition priority. This reduces hidden parser conflicts and makes examples more predictable.

## AP2. Incorrect Parentheses Scope and Modifier Placement

**Problem.** Repetition or optionality modifiers apply to a larger sequence than intended because parentheses include boundary literals.

**Typical symptom.**

- The LLM repeats entire blocks including `start`/`end` markers.
- The parser expects repeated delimiters or accepts malformed block structures.

**Before.**

```text
Section:
    ('start' field1=ID field2=STRING 'end')*
;
```

**After.**

```text
Section:
    'start' (field1=ID field2=STRING)* 'end'
;
```

**Rationale.** Boundary literals should normally be outside repeated or optional groups. Only the variable content should be repeated.

## AP3. Missing Explicit Root Rule

**Problem.** The grammar defines individual components but no complete top-level model structure.

**Typical symptom.**

- The parser consumes the first valid section and then reports `Expected EOF` when later sections appear.
- LLMs cannot infer the required global order or composition of a valid model.

**Before.**

```text
Metadata:
    'Metadata' name=STRING 'end'
;

Entity:
    'Entity' name=ID 'end'
;
```

**After.**

```text
Model:
    metadata=Metadata?
    entities*=Entity
;

Metadata:
    'Metadata' name=STRING 'end'
;

Entity:
    'Entity' name=ID 'end'
;
```

**Rationale.** A root rule tells both the parser and the LLM what a complete model looks like.

## AP4. Rule Declaration Dependency Disorder

**Problem.** Composite or root rules reference rules before those component rules are declared.

**Typical symptom.**

- Unexpected parser failures.
- LLMs see the complete model rule before understanding the components it references.

**Before.**

```text
Model:
    imports*=Import
    entities*=Entity
;

Import:
    'import' uri=STRING
;

Entity:
    'Entity' name=ID 'end'
;
```

**After.**

```text
Import:
    'import' uri=STRING
;

Entity:
    'Entity' name=ID 'end'
;

Model:
    imports*=Import
    entities*=Entity
;
```

**Rationale.** Declaring simpler component rules before composite rules improves readability and can reduce reference/ordering confusion.

## AP5. Non-Standard or Inconsistent Terminology

**Problem.** The grammar uses verbose or unusual names for familiar programming concepts without a domain reason.

**Typical symptom.**

- LLMs mix terminology, e.g., `bool` vs `boolean`, `str` vs `string`.
- Generated models use common conventions that the grammar rejects.

**Before.**

```text
DataType:
    'integer' | 'floatingPoint' | 'boolean'
;
```

**After.**

```text
DataType:
    'int' | 'float' | 'bool'
;
```

**Rationale.** LLMs have strong priors over common programming terminology. Aligning grammar tokens with those priors can improve valid model generation. For non-technical DSLs, verbose natural-language terms may still be appropriate.

## AP6. Unintended Strict Ordering

**Problem.** The grammar forces users to write sections or properties in one fixed order even when order is semantically irrelevant.

**Typical symptom.**

- Models fail only because declarations appear in a different but reasonable order.
- LLMs follow the natural-language prompt order instead of the grammar order.

**Before.**

```text
Model:
    metadata=Metadata?
    brokers*=Broker
    entities*=Entity
    actions*=Action
;
```

**After.**

```text
Model:
    (
        metadata=Metadata?
        brokers*=Broker
        entities*=Entity
        actions*=Action
    )#
;
```

**Rationale.** textX enforces sequence by default. Use unordered groups (`#`) when order should not matter. If order must matter, expose the required top-level order clearly in the prompt and documentation.

## AP7. Inconsistent Block Closure

**Problem.** Some top-level blocks require `end`, while similar blocks do not, or embedded structures are closed like independent declarations.

**Typical symptom.**

- LLMs add or omit `end` inconsistently.
- Validity depends on subtle distinctions that are not visible from examples.

**Before.**

```text
StateTrigger:
    'StateTrigger'
    (
        'entity:' entity=[Entity]
        'property:' property=ID
    )#
    'end'
;
```

**After.**

```text
StateTrigger:
    'StateTrigger'
    (
        'entity:' entity=[Entity]
        'property:' property=ID
    )#
;
```

**Rationale.** Use `end` consistently for independently defined, referenceable top-level blocks. Avoid `end` for embedded configuration fragments that exist only inside a parent rule.

## AP8. Quoted Property Access

**Problem.** Property access rules use `STRING` where `ID` is expected.

**Typical symptom.**

- The grammar requires unnatural syntax such as `sensor."temperature"`.
- LLMs generate natural dot notation such as `sensor.temperature`, which then fails.

**Before.**

```text
Condition:
    entity=[Entity] '.' property=STRING operator=Operator value=Value
;
```

**After.**

```text
Condition:
    entity=[Entity] '.' property=ID operator=Operator value=Value
;
```

**Rationale.** Dot notation normally uses unquoted identifiers. The grammar should match the syntax LLMs and developers naturally expect.

## AP9. Inconsistent Expression Patterns Across Contexts

**Problem.** Semantically equivalent expressions use different syntax in different places.

**Typical symptom.**

- LLMs transfer syntax from one context to another and produce invalid models.
- Users must learn multiple forms for the same conceptual operation.

**Before.**

```text
Condition:
    entity=[Entity] '.' property=ID operator=Operator value=Value
;

Trigger:
    'state:' entity=[Entity] operator=Operator value=Value
;
```

**After.**

```text
PropertyComparison:
    entity=[Entity] '.' property=ID operator=Operator value=Value
;

Condition:
    comparison=PropertyComparison
;

Trigger:
    'state:' comparison=PropertyComparison
;
```

**Rationale.** Reusing the same expression pattern across triggers, conditions, filters, and actions improves predictability and reduces invalid transfer.

## AP10. Left Recursion

**Problem.** A rule directly or indirectly references itself as the leftmost symbol.

**Typical symptom.**

- Parser errors such as maximum recursion depth exceeded.
- LLMs generate nested expressions that the grammar cannot parse.

**Before.**

```text
Expression:
    Expression '+' Term
  | Term
;
```

**After.**

```text
Expression:
    left=Term (operator=('+' | '-') right=Term)*
;
```

**Rationale.** textX cannot handle left recursion. Use base cases plus repetition operators to express repeated or chained expressions.

## AP11. Overly Strict Missing Optionality

**Problem.** Fields that are often omitted in realistic models are required by the grammar.

**Typical symptom.**

- LLMs generate concise valid-looking models that fail because optional metadata, descriptions, units, or configuration fields are missing.

**Before.**

```text
Entity:
    'Entity' name=ID
    'description:' description=STRING
    'freq:' freq=FLOAT
    'end'
;
```

**After.**

```text
Entity:
    'Entity' name=ID
    ('description:' description=STRING)?
    ('freq:' freq=FLOAT)?
    'end'
;
```

**Rationale.** Optionality should reflect actual domain requirements. Making incidental fields mandatory increases invalid generations without improving semantic expressiveness.

## AP12. Missing Alternative Surface Forms

**Problem.** The grammar supports only one wording or structure for a concept that naturally appears in multiple equivalent forms.

**Typical symptom.**

- LLMs generate semantically plausible variants that the grammar rejects.

**Before.**

```text
ComparisonOperator:
    'equals'
;
```

**After.**

```text
ComparisonOperator:
    'equals' | '==' | 'is'
;
```

**Rationale.** For concepts with common equivalent surface forms, carefully adding alternatives can improve robustness. Alternatives should remain controlled to avoid ambiguity.

## Summary Table

| ID | Anti-pattern | Main risk | Typical optimization |
|---|---|---|---|
| AP1 | Ambiguous choice ordering | Wrong alternative selected | Reorder overlapping alternatives |
| AP2 | Incorrect parentheses/modifier scope | Repeated delimiters or malformed blocks | Scope modifiers only over variable content |
| AP3 | Missing root rule | Partial parse / unclear complete model | Add explicit top-level model rule |
| AP4 | Rule dependency disorder | Reference confusion | Declare component rules before composite rules |
| AP5 | Non-standard terminology | LLM uses common rejected terms | Align with target-audience conventions |
| AP6 | Unintended strict ordering | Valid concepts fail due to order | Use unordered groups or document required order |
| AP7 | Inconsistent block closure | Extra/missing `end` | Use consistent closure policy |
| AP8 | Quoted property access | Unnatural rejected dot notation | Use `ID` for property names |
| AP9 | Inconsistent expression patterns | Invalid syntax transfer | Reuse shared expression rules |
| AP10 | Left recursion | Parser recursion failure | Use base cases plus repetition |
| AP11 | Overly strict missing optionality | Concise models rejected | Mark non-essential fields optional |
| AP12 | Missing alternative forms | Plausible variants rejected | Add controlled alternatives |

## Recommended Paper Wording

The methodology targets a catalog of grammar-level anti-patterns that are syntactically legal or locally plausible but reduce downstream LLM model-generation success. These anti-patterns include missing root rules, unintended strict ordering, inconsistent expression patterns, unnatural property access syntax, left recursion, and inconsistent block closure. Each anti-pattern was converted into an explicit prompt-level refinement instruction and, where possible, a validation or repair heuristic. The catalog is not intended to replace formal language engineering judgment; rather, it captures recurring grammar structures that make valid model generation harder for LLMs.
