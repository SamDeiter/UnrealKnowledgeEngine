
from rich.console import Console
from tools.gate.validator import run_validation

console = Console()

def run_gate(engine_path: str, no_capture: bool):
    console.print(f"[bold]Running Gate Validation...[/bold]")
    if engine_path:
        console.print(f"Engine Path: {engine_path}")
    else:
        console.print("[yellow]Warning: No engine path provided. Skipping evidence file checks.[/yellow]")

    report = run_validation(engine_path, no_capture)
    
    console.print(f"[green]Validation complete.[/green]")
    console.print(f"Report saved to [blue]out/gate_report.json[/blue]")
    
    # Summary
    verified_count = sum(1 for v in report.status_map.values() if v == "verified")
    total_count = len(report.status_map)
    console.print(f"Status: {verified_count}/{total_count} LOs verified.")
