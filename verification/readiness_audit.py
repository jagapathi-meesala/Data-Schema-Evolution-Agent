from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
required=["agent.yaml","README.md","SOUL.md","RULES.md","DUTIES.md","AGENTS.md","EXPLAINABILITY.md","requirements.txt",".env.example",".gitignore","pytest.ini","core/__init__.py","core/evolution.py","core/cli.py","tools/compare-schema-versions.yaml","tools/assess-schema-compatibility.yaml","tools/create-migration-checklist.yaml","skills/schema-diff-analysis/SKILL.md","skills/compatibility-assessment/SKILL.md","skills/migration-planning/SKILL.md","tests/test_evolution.py","examples/schema_case.json","verification/readiness_audit.py"]
missing=[p for p in required if not (ROOT/p).is_file()]
assert not missing, f"Missing files: {missing}"
manifest=yaml.safe_load((ROOT/"agent.yaml").read_text())
assert manifest["name"]=="data-schema-evolution-agent"
assert len(manifest["tools"])==3 and all("_" not in x for x in manifest["tools"])
for p in (ROOT/"tools").glob("*.yaml"):
    tool=yaml.safe_load(p.read_text()); assert tool["input_schema"]["type"]=="object" and tool["input_schema"]["additionalProperties"] is False
ex=(ROOT/"EXPLAINABILITY.md").read_text()
for h in ["## Inputs","## Decision","## Limits"]: assert h in ex, h
print("PASS: manifest name normalized")
print("PASS: flat tools listed")
print("PASS: required explainability headings")
print("PASS: strict tool schemas")
print(f"PASS: {len(required)}/{len(required)} required files present")
