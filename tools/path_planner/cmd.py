
import os
import json
import yaml
from typing import List, Dict, Set
from pathlib import Path
from rich.console import Console

console = Console()

class PathPlanner:
    def __init__(self, context_path: str):
        self.context = {}
        if os.path.exists(context_path):
            with open(context_path) as f:
                self.context = json.load(f)
        
        self.los = {}
        self.load_los()

    def load_los(self):
        knowledge_dir = Path("knowledge/learning_objects")
        for root, dirs, files in os.walk(knowledge_dir):
            for file in files:
                if file.endswith(".yml") or file.endswith(".yaml"):
                    try:
                        with open(Path(root) / file) as f:
                            data = yaml.safe_load(f)
                            if "id" in data:
                                self.los[data["id"]] = data
                    except:
                        pass

    def plan(self) -> List[Dict]:
        """
        Deterministic planning:
        1. Context Filtering (Role/Skill) - Skipped for POC simplicity or simple exact match.
        2. Sequence Ordering (Topological)
        """
        # POC Constraint: Concept -> Task -> Troubleshooting
        # We can implement a simple dependency resolver.
        
        visited = set()
        path = []
        
        def visit(lo_id):
            if lo_id in visited:
                return
            if lo_id not in self.los:
                return
            
            lo = self.los[lo_id]
            
            # Visit prerequisites first
            for prereq in lo.get("prerequisites", []):
                visit(prereq)
            
            visited.add(lo_id)
            path.append(lo)

        # Naively try to visit all LOs in the system
        # In a real system, we'd start from a 'goal' or 'root'
        # Here we just want to linearize everything we have.
        # To ensure deterministic order for independent nodes, we sort keys
        sorted_ids = sorted(self.los.keys())
        for lid in sorted_ids:
            visit(lid)
            
        return path

def run_plan(context_path: str):
    console.print(f"[bold]Running Path Planner...[/bold]")
    planner = PathPlanner(context_path)
    path = planner.plan()
    
    out_dir = Path("out/path")
    os.makedirs(out_dir, exist_ok=True)
    
    # Write JSON
    path_data = {
        "context": planner.context,
        "steps": [lo["id"] for lo in path],
        "details": path
    }
    with open(out_dir / "path.json", "w") as f:
        json.dump(path_data, f, indent=2)
    
    # Write Markdown
    md_content = "# Generated Learning Path\n\n"
    md_content += f"**Context**: {json.dumps(planner.context)}\n\n"
    
    for i, lo in enumerate(path, 1):
        md_content += f"## {i}. {lo['title']}\n"
        md_content += f"- **ID**: `{lo['id']}`\n"
        md_content += f"- **Type**: {lo['type']}\n"
        md_content += f"- **Description**: {lo['description']}\n\n"
        md_content += f"> Reasoning: Included based on prerequisites {lo.get('prerequisites', [])}\n\n"

    with open(out_dir / "path.md", "w") as f:
        f.write(md_content)

    console.print(f"[green]Plan generated: {len(path)} steps.[/green]")
    console.print(f"- out/path/path.json")
    console.print(f"- out/path/path.md")
