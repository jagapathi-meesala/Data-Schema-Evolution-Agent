# Explainability

## Inputs
The agent accepts two field-based schema snapshots. Each snapshot has optional `name` and `version` plus a `fields` array. Each field needs `name` and `type`; `required` and `nullable` are optional booleans.

## Decision
It compares field names and the supplied type, requiredness, and nullability properties. It labels removals, type changes, newly required fields, and nullability tightening as breaking candidates. The labels are conservative heuristics, not format-specific compatibility results.

## Limits
The agent does not parse all features of Avro, Protobuf, SQL DDL, or JSON Schema. It does not query registries or discover real consumers. Run the relevant platform validator and contract tests before rollout.

## Tool: compare-schema-versions
### Inputs and Data Sources
Old and new field-based schema snapshots supplied by the caller.
### Decision and Reasoning
Compares fields by name and checks type, requiredness, and nullability.
### Outputs and Evidence
A list of changes, heuristic risk labels, and supporting facts from the snapshots.
### Limits and Constraints
Does not infer defaults, aliases, nested compatibility, or format-specific rules.
### Failure Handling
Returns `invalid_input` when the snapshot structure or field data is invalid.
### Human Review
Verify results against the actual schema format and consumer behavior.

## Tool: assess-schema-compatibility
### Inputs and Data Sources
A diff result and a requested backward, forward, or full review mode.
### Decision and Reasoning
Flags review when any change is classified as a breaking candidate.
### Outputs and Evidence
Review status, flagged changes, and required validation checks.
### Limits and Constraints
Does not calculate formal compatibility for any schema format.
### Failure Handling
Returns `invalid_input` for unsupported modes and `unknown` for invalid diffs.
### Human Review
Run the actual registry or format-specific compatibility checker.

## Tool: create-migration-checklist
### Inputs and Data Sources
A schema diff and optional owner label.
### Decision and Reasoning
Maps observed change types to suggested backfill, deprecation, and testing tasks.
### Outputs and Evidence
An ordered checklist and an explicit approval requirement.
### Limits and Constraints
Does not execute changes or know production topology.
### Failure Handling
Produces general review steps when the diff contains no changes.
### Human Review
Assign owners, validate operational steps, and approve rollout separately.
