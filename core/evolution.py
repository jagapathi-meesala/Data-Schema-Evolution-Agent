"""Schema snapshot diffing and conservative compatibility review."""
from __future__ import annotations

SUPPORTED_TYPES = {"string", "integer", "number", "boolean", "object", "array", "null"}

def _valid_schema(schema):
    if not isinstance(schema, dict): return False, "Schema must be an object."
    if not isinstance(schema.get("fields"), list): return False, "Schema must contain a fields list."
    seen=set()
    for field in schema["fields"]:
        if not isinstance(field, dict) or not isinstance(field.get("name"), str) or not field["name"]:
            return False, "Each field must have a non-empty string name."
        if field["name"] in seen: return False, f"Duplicate field name: {field['name']}"
        seen.add(field["name"])
        if field.get("type") not in SUPPORTED_TYPES: return False, f"Unsupported or missing type for field {field['name']}."
        if "required" in field and not isinstance(field["required"], bool): return False, f"required must be boolean for field {field['name']}."
    return True, ""

def compare_schema_versions(old_schema: dict, new_schema: dict) -> dict:
    """Compare simple field-based schema snapshots; input format is documented in README."""
    for label, schema in (("old_schema", old_schema), ("new_schema", new_schema)):
        ok, reason = _valid_schema(schema)
        if not ok: return {"status":"invalid_input", "invalid_schema":label, "reason":reason, "changes":[], "limitations":["No compatibility conclusion is made for invalid schema input."]}
    old={f["name"]:f for f in old_schema["fields"]}; new={f["name"]:f for f in new_schema["fields"]}
    changes=[]
    for name in sorted(old.keys()-new.keys()):
        changes.append({"field":name,"change":"removed","old_type":old[name]["type"],"new_type":None,"risk":"breaking_candidate","evidence":"Field exists in old schema and is absent in new schema."})
    for name in sorted(new.keys()-old.keys()):
        f=new[name]; required=f.get("required",False)
        changes.append({"field":name,"change":"added","old_type":None,"new_type":f["type"],"risk":"breaking_candidate" if required else "usually_compatible_candidate","evidence":"Field exists only in new schema; required="+str(required)+"."})
    for name in sorted(old.keys()&new.keys()):
        a,b=old[name],new[name]
        if a["type"] != b["type"]:
            changes.append({"field":name,"change":"type_changed","old_type":a["type"],"new_type":b["type"],"risk":"breaking_candidate","evidence":"Field type differs between snapshots; conversion and consumer behavior need review."})
        old_req=a.get("required",False); new_req=b.get("required",False)
        if old_req != new_req:
            risk="breaking_candidate" if new_req else "relaxation_candidate"
            changes.append({"field":name,"change":"requiredness_changed","old_required":old_req,"new_required":new_req,"risk":risk,"evidence":"Requiredness flag differs between snapshots."})
        if a.get("nullable",False) != b.get("nullable",False):
            changes.append({"field":name,"change":"nullability_changed","old_nullable":a.get("nullable",False),"new_nullable":b.get("nullable",False),"risk":"breaking_candidate" if not b.get("nullable",False) else "relaxation_candidate","evidence":"Nullability flag differs between snapshots."})
    risky=sum(c["risk"]=="breaking_candidate" for c in changes)
    return {"status":"changes_detected" if changes else "no_structural_changes_detected","old_version":old_schema.get("version"),"new_version":new_schema.get("version"),"change_count":len(changes),"breaking_candidates":risky,"changes":changes,"compatibility_note":"Heuristic only: actual compatibility depends on format, reader/writer mode, defaults, constraints, and downstream consumers.","limitations":["Supports field-based snapshots, not every Avro, Protobuf, SQL, or JSON Schema feature.","Type changes are conservatively flagged; widening/narrowing semantics are not inferred.","No live registry, pipeline, or consumer inventory is queried."]}

def assess_schema_compatibility(diff: dict, mode: str = "backward") -> dict:
    if mode not in {"backward","forward","full"}:
        return {"status":"invalid_input","reason":"mode must be backward, forward, or full."}
    if diff.get("status")=="invalid_input": return {"status":"unknown","reason":"Cannot assess an invalid schema diff."}
    breaking=[c for c in diff.get("changes",[]) if c.get("risk")=="breaking_candidate"]
    if breaking:
        status="review_required"
    else: status="no_breaking_candidates_detected"
    return {"mode":mode,"status":status,"breaking_candidates":breaking,"review_checks":["Confirm serializer and deserializer rules for the actual schema format.","Run compatibility checks against the registry or platform used in production.","Test representative historical and new payloads with downstream consumers.","Verify defaults, null handling, constraints, and field aliases where supported."],"limitations":["This is not a formal format-specific compatibility guarantee.","The same change may behave differently under backward, forward, or full compatibility rules."]}

def create_migration_checklist(diff: dict, owner: str = "unassigned") -> dict:
    changes=diff.get("changes",[]); steps=[]
    if not changes: steps.append("Confirm that the snapshots are complete and no external constraints changed.")
    for c in changes:
        field=c.get("field","unknown")
        if c.get("change")=="removed": steps.append(f"Find consumers of '{field}' and plan deprecation before removal.")
        elif c.get("change")=="added" and c.get("risk")=="breaking_candidate": steps.append(f"Provide a safe default or coordinated rollout for required field '{field}'.")
        elif c.get("change")=="type_changed": steps.append(f"Define and test conversion/backfill for '{field}' from {c.get('old_type')} to {c.get('new_type')}.")
        elif c.get("change")=="requiredness_changed" and c.get("new_required"): steps.append(f"Backfill and validate '{field}' before enforcing requiredness.")
        elif c.get("change")=="nullability_changed" and c.get("new_nullable") is False: steps.append(f"Check existing null values in '{field}' before disallowing nulls.")
        elif c.get("change")=="added": steps.append(f"Verify default/optional handling for new field '{field}'.")
        else: steps.append(f"Review consumer impact and tests for '{field}' change ({c.get('change')}).")
    steps += ["Run schema-format-specific compatibility validation.","Run producer and consumer contract tests in a non-production environment.","Document rollout, rollback, ownership, and monitoring plans."]
    return {"owner":owner,"change_count":len(changes),"checklist":list(dict.fromkeys(steps)),"approval_required":True,"decision_boundary":"Checklist generation does not apply migrations or approve a production rollout."}
