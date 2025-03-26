import bpy
import json
import os

def convert_idprops_to_python(value):
    """
    Recursively convert Blender's ID properties into basic Python types
    that can be serialized by json.dump().
    """
    # Basic serializable types:
    if isinstance(value, (str, int, float, bool, type(None))):
        return value

    # Convert list or tuple items
    elif isinstance(value, (list, tuple)):
        return [convert_idprops_to_python(v) for v in value]

    # If it's an IDPropertyGroup or a similar mapping type, convert to dict
    elif hasattr(value, "keys") and hasattr(value, "__getitem__"):
        d = {}
        for k in value.keys():
            d[k] = convert_idprops_to_python(value[k])
        return d

    # Fallback: just store string representation
    else:
        return str(value)

def export_rig_hierarchy(armature_name, output_path):
    """
    Export the hierarchy, constraints, and custom properties of an Armature object into a JSON file.
    Only constraints of certain types are included:
        COPY_LOCATION, COPY_ROTATION, COPY_TRANSFORMS, TRANSFORM, STRETCH_TO,
        ACTION, ARMATURE, CHILD_OF, PIVOT, IK, LIMIT_ROTATION
    armature_name: Name of the armature object in the scene (string).
    output_path: File path where the JSON data will be saved (string).
    """

    # Find the armature object by name
    arm_obj = bpy.data.objects.get(armature_name)
    if arm_obj is None:
        raise ValueError(f"No object named '{armature_name}' found in the current scene.")

    if arm_obj.type != 'ARMATURE':
        raise TypeError(f"Object '{arm_obj.name}' is not an Armature.")

    # Define which constraint types to include
    allowed_constraint_types = {
        "COPY_LOCATION",
        "COPY_ROTATION",
        "COPY_TRANSFORMS",
        "TRANSFORM",
        "STRETCH_TO",
        "ACTION",
        "ARMATURE",
        "CHILD_OF",
        "PIVOT",
        "IK",
        "LIMIT_ROTATION",
        "COPY_SCALE",
        "LIMIT_DISTANCE",
        "DAMPED_TRACK"
    }


    # Build the export data structure
    arm_data = {
        "object_name": arm_obj.name,
        "possible_constraint_types": list(allowed_constraint_types),
        "bones": []
    }

    # Iterate over pose bones
    for pbone in arm_obj.pose.bones:
        bone_info = {
            "name": pbone.name,
            "parent": pbone.parent.name if pbone.parent else None,
            "constraints": [],
            "custom_properties": {}
        }

        # Gather only the allowed constraints
        for c in pbone.constraints:
            if c.type in allowed_constraint_types:
                c_info = {
                    "name": c.name,
                    "type": c.type,
                    "influence": c.influence
                }
                bone_info["constraints"].append(c_info)

        # Gather custom properties, converting them to JSON-serializable formats
        for prop_name in pbone.keys():
            value = pbone[prop_name]
            bone_info["custom_properties"][prop_name] = convert_idprops_to_python(value)

        arm_data["bones"].append(bone_info)

    # Write the data to a JSON file
    with open(output_path, "w") as f:
        json.dump(arm_data, f, indent=4)

    print(f"Rig data for '{armature_name}' exported to: {output_path}")


def verify_exported_constraints(json_path, armature_name):
    """
    Loads the JSON file and compares the constraints for each bone
    with those found in the Blender scene for the specified armature.
    Prints any mismatches or missing bones.
    """
    # Load the exported JSON file
    if not os.path.exists(json_path):
        print(f"JSON file not found at {json_path}")
        return

    with open(json_path, 'r') as f:
        exported_data = json.load(f)

    # Get the armature object
    arm_obj = bpy.data.objects.get(armature_name)
    if not arm_obj:
        print(f"Armature '{armature_name}' not found in the current scene.")
        return

    # Create a quick mapping from bone name -> constraints (by name)
    scene_bone_constraints = {}
    for pbone in arm_obj.pose.bones:
        constraint_names = [c.name for c in pbone.constraints]
        scene_bone_constraints[pbone.name] = constraint_names

    # Compare exported constraints to scene constraints
    for bone_data in exported_data.get('bones', []):
        bone_name = bone_data['name']
        exported_constraints = [c['name'] for c in bone_data.get('constraints', [])]

        if bone_name not in scene_bone_constraints:
            print(f"Bone '{bone_name}' not found in armature. (Possibly hidden or removed.)")
            continue

        actual_constraints = scene_bone_constraints[bone_name]

        if set(exported_constraints) == set(actual_constraints):
            print(f"Bone '{bone_name}' constraints match.")
        else:
            print(f"Bone '{bone_name}' mismatch!\n  Exported: {exported_constraints}\n  Actual:   {actual_constraints}")

def main():
    # Build the file path in the same directory as the .blend file
    blend_dir = bpy.path.abspath("//")  # directory where the current .blend is located
    json_path = os.path.join(blend_dir, "model_tree.json")
    armature_name = "ClassicMan_Rigify"

    # 1. Export the rig hierarchy to JSON
    export_rig_hierarchy(armature_name, json_path)

    # 2. Verify the constraints by re-reading the JSON and comparing to the current scene
    verify_exported_constraints(json_path, armature_name)

if __name__ == "__main__":
    main()
