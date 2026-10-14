# Data Schema Evolution Agent

An OpenGAP-style agent project that compares field-based schema snapshots, flags candidate compatibility risks, and creates a migration-review checklist.

## Features
- Field addition/removal comparison
- Type, requiredness, and nullability change detection
- Backward/forward/full review modes
- Evidence-backed findings and migration checklist
- Strict YAML tool schemas, skills, tests, and readiness audit

## Schema input format
Provide JSON with `old_schema` and `new_schema`; each schema has `fields`, a list of objects containing `name`, `type`, and optional boolean `required` and `nullable`. Supported types: string, integer, number, boolean, object, array, null. Example: `examples/schema_case.json`.

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python3 verification/readiness_audit.py
python3 -m core.cli examples/schema_case.json
```

## Safety and limitations
This is heuristic schema review, not a formal compatibility guarantee. Actual behavior depends on schema format, reader/writer direction, defaults, aliases, constraints, and downstream consumers. Validate with the platform's schema registry or format-specific tool and run producer/consumer contract tests. The agent never applies migrations or approves production rollout.
