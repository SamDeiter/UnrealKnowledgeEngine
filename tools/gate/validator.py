
import os
import yaml
import json
from enum import Enum
from typing import List, Dict, Any
from pathlib import Path
from pydantic import ValidationError
from tools.gate.models import LearningObject, EvidenceItem

class ValidationStatus(str, Enum):
    VERIFIED = "verified"
    NEEDS_REVIEW = "needs_review"
    INVALID = "invalid"
    STALE = "stale"

class GateReport:
    def __init__(self):
        self.results = {}
        self.status_map = {}

    def add_result(self, lo_id: str, status: ValidationStatus, errors: List[str] = None):
        self.results[lo_id] = {
            "status": status,
            "errors": errors or []
        }
        self.status_map[lo_id] = status

    def save(self, report_path: str, status_path: str):
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2)
        with open(status_path, "w") as f:
            json.dump(self.status_map, f, indent=2)

def validate_lo_file(file_path: Path, engine_root: Path = None, skip_evidence: bool = False) -> (ValidationStatus, List[str]):
    errors = []
    
    # 1. Parse YAML
    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return ValidationStatus.INVALID, [f"YAML Parse Error: {str(e)}"]

    # 2. Validate Schema
    try:
        lo = LearningObject(**data)
    except ValidationError as e:
        return ValidationStatus.INVALID, [f"Schema Error: {str(e)}"]

    # 3. Validate Evidence Paths (if engine provided)
    if engine_root and not skip_evidence:
        for ev in lo.evidence:
            full_path = engine_root / ev.file
            if not full_path.exists():
                errors.append(f"Evidence file not found: {ev.file}")
    
    if errors:
        return ValidationStatus.INVALID, errors
    
    return ValidationStatus.VERIFIED, []

def run_validation(engine_root: str, no_capture: bool):
    knowledge_dir = Path("knowledge/learning_objects")
    report = GateReport()
    
    engine_path = Path(engine_root) if engine_root else None
    
    # Walk through LOs
    for root, dirs, files in os.walk(knowledge_dir):
        for file in files:
            if file.endswith(".yml") or file.endswith(".yaml"):
                full_path = Path(root) / file
                status, errors = validate_lo_file(full_path, engine_path, no_capture)
                
                # Extract ID from filename or content (using content as source of truth for ID)
                # But we need basic parsing first. We already parsed it in validate_lo_file effectively.
                # Let's do a quick re-parse to get the ID for the report key.
                try:
                    with open(full_path, "r") as f:
                        data = yaml.safe_load(f)
                        lo_id = data.get("id", file)
                except:
                    lo_id = file

                report.add_result(lo_id, status, errors)

    # Ensure output dir exists
    os.makedirs("out", exist_ok=True)
    report.save("out/gate_report.json", "out/status.json")
    return report
