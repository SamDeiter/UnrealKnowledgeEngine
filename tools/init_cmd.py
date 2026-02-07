
import os
import json
from rich.console import Console

console = Console()

def run_init():
    console.print("[bold green]Initializing UKE environment...[/bold green]")
    
    # Ensure directories exist
    dirs = [
        "knowledge/learning_objects/staticmesh",
        "knowledge/assets/overlays/staticmesh.collision.simple",
        "tools/gate",
        "tools/freshness/hash_verify",
        "tools/freshness/auto_heal",
        "tools/capture/scripts",
        "tools/capture/plugin/TutorialCapture",
        "tools/path_planner",
        "tools/site_gen",
        "out/images",
        "out/site",
        "out/audit",
        "out/path",
        "tests"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        console.print(f"Verified directory: [blue]{d}[/blue]")

    # Create context.json if not exists
    context_path = "context.json"
    if not os.path.exists(context_path):
        default_context = {
            "user_role": "technical_artist",
            "project_phase": "production",
            "skill_level": "intermediate"
        }
        with open(context_path, "w") as f:
            json.dump(default_context, f, indent=2)
        console.print(f"Created [blue]{context_path}[/blue]")
    else:
        console.print(f"[yellow]{context_path} already exists[/yellow]")

    console.print("[bold green]Initialization complete.[/bold green]")
