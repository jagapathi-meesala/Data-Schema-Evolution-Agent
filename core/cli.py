"""Command-line interface for sample schema evolution review."""
import json, sys
from pathlib import Path
from .evolution import compare_schema_versions, assess_schema_compatibility, create_migration_checklist

def main():
    if len(sys.argv)!=2:
        print("Usage: python -m core.cli examples/schema_case.json", file=sys.stderr); return 2
    try: data=json.loads(Path(sys.argv[1]).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error":str(exc)})); return 2
    diff=compare_schema_versions(data.get("old_schema"),data.get("new_schema"))
    result={"diff":diff,"compatibility":assess_schema_compatibility(diff,data.get("mode","backward")),"migration_checklist":create_migration_checklist(diff,data.get("owner","unassigned"))}
    print(json.dumps(result,indent=2)); return 0 if diff.get("status")!="invalid_input" else 1

if __name__=="__main__": raise SystemExit(main())
