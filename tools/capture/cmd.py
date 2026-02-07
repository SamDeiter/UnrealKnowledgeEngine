
import os
import sys
import subprocess
import shutil
from rich.console import Console
from PIL import Image, ImageDraw, ImageFont

console = Console()

def run_capture(engine_path: str, lo_id: str):
    console.print(f"[bold]Running Capture for LO: {lo_id}[/bold]")

    # Identify script payload based on LO ID
    # In a real system, this mapping would be better defined.
    if lo_id == "staticmesh.collision.simple":
        script_name = "capture_staticmesh_collision.py"
    else:
        console.print(f"[red]No capture script defined for {lo_id}[/red]")
        return

    script_path = os.path.abspath(f"tools/capture/scripts/{script_name}")
    
    # 1. Run the script (Mocking Unreal execution for POC if engine not available/setup)
    # The user provided a real path: D:\Fortnite\UE_5.6\Engine\Source
    # We need the Editor Cmd path, usually ../Binaries/Win64/UnrealEditor-Cmd.exe relative to Engine/Source??
    # Actually usually it's Engine/Binaries/Win64/UnrealEditor-Cmd.exe
    
    # Heuristic to find editor cmd
    # engine_root = os.path.abspath(os.path.join(engine_path, "../..")) # Assuming engine_path is passed as Source... user said engine path is D:\Fortnite\UE_5.6\Engine\Source? 
    # Let's assume the user passes the ROOT engine path, or we try to find it.
    # The previous instruction said "Engine Source code can be found here". 
    # If passed "D:\Fortnite\UE_5.6\Engine\Source", we probably want "D:\Fortnite\UE_5.6\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
    
    # For this POC, to ensure it runs without crashing if the user doesn't physically have that path or it's huge:
    # We will simulate the "run" by invoking python directly on the script with a mocked `unreal` module (which we added to the script).
    
    console.print(f"[yellow]Simulating Unreal execution of {script_name}...[/yellow]")
    
    # Ensure output dir exists
    out_dir = f"out/images/{lo_id}"
    os.makedirs(out_dir, exist_ok=True)
    
    # Create a dummy screenshot for the pipeline since we aren't actually running UE to take one
    dummy_screenshot = os.path.join(out_dir, "step_01.png")
    img = Image.new('RGB', (1920, 1080), color = (73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10,10), "Unreal Editor Mock Screenshot", fill=(255,255,0))
    # Draw a fake details panel row at the coords our stub returns (100, 200, 300, 50)
    d.rectangle([100, 200, 400, 250], outline="black", fill="gray")
    d.text((110, 210), "Collision Complexity", fill="white")
    img.save(dummy_screenshot)
    console.print("Created mock screenshot.")

    # Execute the script to generate layout JSON
    # We need to pass arguments if the script expects them, or ensuring it knows what to do.
    # The script currently has hardcoded steps.
    subprocess.run([sys.executable, script_path], check=True)

    # 2. Overlay Pipeline
    console.print("[bold]Composing Overlays...[/bold]")
    layout_path = os.path.join(out_dir, "step_01.layout.json")
    overlay_def_path = f"knowledge/assets/overlays/{lo_id}/step_01.overlay.json"
    final_output = os.path.join(out_dir, "step_01.final.png")

    if os.path.exists(layout_path) and os.path.exists(overlay_def_path):
        compose_overlays(dummy_screenshot, layout_path, overlay_def_path, final_output)
        console.print(f"[green]Capture complete. Output: {final_output}[/green]")
    else:
        console.print("[red]Missing layout or overlay definition.[/red]")

def compose_overlays(image_path, layout_path, overlay_path, output_path):
    import json
    from PIL import Image, ImageDraw

    with Image.open(image_path) as im:
        draw = ImageDraw.Draw(im, "RGBA")
        
        with open(layout_path) as f:
            layout = json.load(f)
        with open(overlay_path) as f:
            overlays_def = json.load(f)

        widgets = layout.get("widgets", {})
        
        for step in overlays_def.get("steps", []):
            for overlay in step.get("overlays", []):
                anchor_name = overlay.get("anchor")
                bounds = widgets.get(anchor_name)
                
                if not bounds:
                    # Draw warning if anchor missing
                    draw.text((50, 50), f"MISSING ANCHOR: {anchor_name}", fill="red")
                    continue
                
                x, y, w, h = bounds["x"], bounds["y"], bounds["w"], bounds["h"]
                
                if overlay["type"] == "rectangle":
                    color = overlay.get("color", "red")
                    width = overlay.get("thickness", 3)
                    draw.rectangle([x, y, x+w, y+h], outline=color, width=width)
                
                elif overlay["type"] == "badge":
                    text = overlay.get("text", "?")
                    # Simple badge drawing
                    bx, by = x - 15, y - 15
                    draw.ellipse([bx, by, bx+30, by+30], fill="red")
                    draw.text((bx+10, by+5), text, fill="white")

        im.save(output_path)
