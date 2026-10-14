import json
from pathlib import Path
from core.evolution import compare_schema_versions, assess_schema_compatibility, create_migration_checklist

def test_example_flags_type_and_required_addition():
    data=json.loads(Path("examples/schema_case.json").read_text())
    diff=compare_schema_versions(data["old_schema"],data["new_schema"])
    assert diff["status"]=="changes_detected"
    assert diff["breaking_candidates"] >= 2

def test_identical_schema_has_no_changes():
    s={"fields":[{"name":"id","type":"string","required":True}]}
    assert compare_schema_versions(s,s)["status"]=="no_structural_changes_detected"

def test_removed_field_is_flagged():
    d=compare_schema_versions({"fields":[{"name":"x","type":"integer"}]},{"fields":[]})
    assert d["changes"][0]["change"]=="removed"

def test_duplicate_field_rejected():
    s={"fields":[{"name":"x","type":"string"},{"name":"x","type":"string"}]}
    assert compare_schema_versions(s,{"fields":[]})["status"]=="invalid_input"

def test_unknown_type_rejected():
    assert compare_schema_versions({"fields":[{"name":"x","type":"magic"}]},{"fields":[]})["status"]=="invalid_input"

def test_compatibility_mode_validation():
    assert assess_schema_compatibility({"changes":[]},"sideways")["status"]=="invalid_input"

def test_review_required_for_breaking_candidate():
    result=assess_schema_compatibility({"changes":[{"field":"x","risk":"breaking_candidate"}]})
    assert result["status"]=="review_required"

def test_checklist_requires_approval():
    result=create_migration_checklist({"changes":[{"field":"id","change":"removed"}]},"team")
    assert result["approval_required"] is True and any("deprecation" in x for x in result["checklist"])

def test_invalid_input_report_is_safe():
    result=compare_schema_versions(None,{"fields":[]})
    assert result["status"]=="invalid_input"
