
import os
import hashlib
import re
import json
import datetime
from pathlib import Path
from rich.console import Console

console = Console()

def normalize_snippet(snippet: str) -> str:
    """
    Normalizes a code snippet for hashing.
    1. Remove single-line comments //...
    2. Remove multi-line comments /*...*/
    3. Remove all whitespace (spaces, tabs, newlines)
    """
    # Remove single line comments
    snippet = re.sub(r'//.*', '', snippet)
    # Remove multi-line comments
    snippet = re.sub(r'/\*.*?\*/', '', snippet, flags=re.DOTALL)
    # Remove all whitespace
    snippet = re.sub(r'\s+', '', snippet)
    return snippet

def compute_hash(snippet: str) -> str:
    normalized = normalize_snippet(snippet)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def extract_snippet_window(file_path: Path, symbol: str, context_lines: int = 40) -> str:
    """
    Simulates finding a symbol and extracting a window around it.
    For POC: we'll just read the file and look for the string literal "symbol".
    If found, return X lines around it.
    If file doesn't exist (because we are mocking engine), return a dummy string if we are in test mode
    or raise error.
    """
    if not file_path.exists():
        # POC Fallback logic: if the engine path is "D:\Fortnite...", we might not have access in this env.
        # But for 'heal', we assume we do. If we don't, we can't really hash.
        # However, for the purpose of the POC demo running completely, we might need a fallback.
        # User requirement: "No hallucinated evidence".
        # But if the user runs this on a machine WITHOUT the engine, it will fail.
        # We will assume it fails if not found, consistent with requirements.
        raise FileNotFoundError(f"Engine file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Simple substrings search for symbol
    idx = content.find(symbol)
    if idx == -1:
        # Retry with some fuzzy matching or just fail?
        # POC: fail
        raise ValueError(f"Symbol '{symbol}' not found in {file_path}")

    # Extract lines
    # Convert index to line number
    pre_content = content[:idx]
    line_num = pre_content.count('\n')
    
    lines = content.splitlines()
    start_line = max(0, line_num - (context_lines // 2))
    end_line = min(len(lines), line_num + (context_lines // 2))
    
    return "\n".join(lines[start_line:end_line])

def run_heal(engine_root: str, from_sha: str, to_sha: str):
    console.print(f"[bold]Running Auto-Heal...[/bold]")
    console.print(f"Engine: {engine_root}")
    console.print(f"Diff: {from_sha} -> {to_sha}")

    # In a real tool, we would:
    # 1. Load all LOs.
    # 2. Identify LOs that touch files changed between from_sha and to_sha.
    # 3. For each affected LO, extract the new snippet and hash it.
    # 4. Compare with the hash in the YAML.
    
    # For POC Vertical Slice:
    # We will iterate over our known 3 LOs and perform the check on their evidence.
    
    import yaml
    from tools.gate.models import LearningObject
    
    audit_dir = Path("out/audit")
    os.makedirs(audit_dir, exist_ok=True)
    
    knowledge_dir = Path("knowledge/learning_objects")
    engine_path = Path(engine_root)
    
    lo_checked = 0
    healed_count = 0
    review_count = 0
    
    for root, dirs, files in os.walk(knowledge_dir):
        for file in files:
            if file.endswith(".yml") or file.endswith(".yaml"):
                full_path = Path(root) / file
                with open(full_path, "r") as f:
                    data = yaml.safe_load(f)
                
                try:
                    lo = LearningObject(**data)
                except:
                    continue
                
                lo_checked += 1
                
                for ev in lo.evidence:
                    full_ev_path = engine_path / ev.file
                    
                    try:
                        current_snippet = extract_snippet_window(full_ev_path, ev.symbol)
                        current_hash = compute_hash(current_snippet)
                        
                        # In a real scenario, we compare current_hash against ev.snippet_hash.
                        # If matches: Verification Pass.
                        # If mismatch:
                        #   We would ideally check if the AST is effectively the same (mechanical drift).
                        #   For this POC context: "Normalized snippet hashing only".
                        #   So if normalized hash matches, it IS mechanical match.
                        
                        # Wait, ev.snippet_hash in the YAML is the 'verified' hash.
                        # If current_hash == ev.snippet_hash, then NO CHANGE (or only whitespace change if we normalized before hashing).
                        # If we stripped whitespace in normalization, then whitespace changes result in SAME hash.
                        # So:
                        # 1. Calculate Hash of file content (normalized).
                        # 2. Compare with YAML hash.
                        # 3. If Match: It's good (either identical or just formatting).
                        # 4. If Mismatch: It's semantic change -> Needs Review.
                        
                        if current_hash == ev.snippet_hash:
                            # It matches our normalized view.
                            # We can log a "Verified" audit.
                            action = "VERIFIED"
                            status = "verified"
                        else:
                            # Mismatch
                            action = "FLAGGED"
                            status = "needs_review"
                            review_count += 1
                        
                        # Audit Log
                        audit_entry = {
                            "timestamp": datetime.datetime.now().isoformat(),
                            "lo_id": lo.id,
                            "symbol": ev.symbol,
                            "file": ev.file,
                            "old_hash": ev.snippet_hash,
                            "new_hash": current_hash,
                            "action": action,
                            "reason": "Normalized hash comparison"
                        }
                        
                        audit_filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{lo.id}.json"
                        with open(audit_dir / audit_filename, "w") as af:
                            json.dump(audit_entry, af, indent=2)
                            
                        console.print(f"[{'green' if action=='VERIFIED' else 'red'}] {lo.id}: {action}[/]")

                    except Exception as e:
                        console.print(f"[red]Error checking {lo.id}: {e}[/red]")
                        # Log error audit
                        json.dump({"error": str(e), "lo_id": lo.id}, open(audit_dir / f"error_{lo.id}.json", "w"))

    console.print(f"Heal complete. Checked {lo_checked} LOs. Flagged {review_count} for review.")
    
    # Update status summary
    # (In a real system we would merge this with existing status)
