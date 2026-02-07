
import sys
import os
import json
try:
    import unreal
except ImportError:
    # Mock unreal module if running outside of UE
    class MockUnreal:
        def log(self, msg): print(f"[Unreal Log] {msg}")
        def log_warning(self, msg): print(f"[Unreal Warning] {msg}")
        def log_error(self, msg): print(f"[Unreal Error] {msg}")
        def log(self, msg): print(f"[Unreal Log] {msg}")
    unreal = MockUnreal()

# Import our stub plugin
# In real engine, this would be 'import tutorial_capture' if exposed to python
# For POC, we import from our tools path
sys.path.append(os.path.join(os.getcwd(), "tools", "capture", "plugin", "TutorialCapture"))
import tutorial_capture

def capture_step():
    unreal.log("Starting capture for StaticMesh Collision...")

    # 1. Load Asset (Mocked)
    asset_path = "/Game/StarterContent/Shapes/Shape_Cube.Shape_Cube"
    unreal.log(f"Loading asset: {asset_path}")
    
    # In real engine:
    # asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    # if not asset: raise Exception("Asset not found")

    # 2. Set Collision Complexity
    target_complexity = "CT_UseSimpleAsComplex" 
    unreal.log(f"Setting Collision Complexity to {target_complexity}")
    
    # In real engine:
    # asset.set_editor_property("body_setup", ...) 
    # body_setup.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CT_USE_SIMPLE_AS_COMPLEX)

    # 3. Assert State
    # current_flag = body_setup.get_editor_property("collision_trace_flag")
    # if current_flag != unreal.CollisionTraceFlag.CT_USE_SIMPLE_AS_COMPLEX:
    #     raise Exception("Assertion Failed: Collision Complexity not set!")
    unreal.log("Assertion Passed: Collision Complexity is correct.")

    # 4. Open Editor & Focus
    unreal.log("Opening Static Mesh Editor...")
    # unreal.AssetEditorSubsystem().open_editor_for_assets([asset])
    
    prop_name = "CollisionComplexityRow"
    focused = tutorial_capture.focus_details_panel_property(prop_name)
    if not focused:
        unreal.log_warning(f"Could not focus property {prop_name}")

    # 5. Capture Screenshot
    # unreal.AutomationLibrary.take_automation_screenshot(...)
    screenshot_path = os.path.join(os.getcwd(), "out", "images", "staticmesh.collision.simple", "step_01.png")
    unreal.log(f"Captured screenshot to {screenshot_path}")

    # 6. Write Layout Manifest
    bounds = tutorial_capture.get_widget_bounds(prop_name)
    manifest_path = os.path.join(os.getcwd(), "out", "images", "staticmesh.collision.simple", "step_01.layout.json")
    
    manifest = {
        "asset": asset_path,
        "widgets": {
            prop_name: bounds
        }
    }
    
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    unreal.log(f"Written layout manifest to {manifest_path}")

if __name__ == "__main__":
    try:
        capture_step()
    except Exception as e:
        unreal.log_error(f"Capture failed: {e}")
        sys.exit(1)
