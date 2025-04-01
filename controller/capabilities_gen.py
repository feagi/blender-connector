import bpy 
import json
import os 
import math

def compute_bone_length(bone):
    """
    Computes the length of a bone using its head and tail coordinates.
    Parameters:
        bone: A Blender pose bone.
        
    Returns:
        float: The computed length of the bone.
    """
    head = bone.bone.head  # (x, y, z) coordinates
    tail = bone.bone.tail
    dx = tail[0] - head[0]
    dy = tail[1] - head[1]
    dz = tail[2] - head[2]
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def compute_gyro_range(bone):
    """
    Computes a custom gyro range to the bone's length.
    
    Parameters:
        bone: A Blender pose bone.
        
    Returns:
        dict: A dictionary with keys "max_value" and "min_value".
    """

    length = compute_bone_length(bone)
    k = 0.5  # Adjust this constant to scale the dynamic range as needed.
    
    # Avoid division by zero by setting a minimum length value.
    if length < 1e-6:
        dynamic_range = k  # Or some default value.
    else:
        dynamic_range = k / length
        
    return {"max_value": dynamic_range, "min_value": -dynamic_range} 

def compute_servo_range(bone):
    """
    Computes a custom gyro range to the bone's length.
    
    Parameters:
        bone: A Blender pose bone.
        
    Returns:
        dict: A dictionary with keys "max_value" and "min_value".
    """

    length = compute_bone_length(bone)
    k = 0.5  # Adjust this constant to scale the dynamic range as needed.
    
    # Avoid division by zero by setting a minimum length value.
    if length < 1e-6:
        dynamic_range = k  # Or some default value.
    else:
        dynamic_range = k / length
        
    return {"max_value": dynamic_range, "min_value": -dynamic_range} 

def generate_capabilities_json(armature_name, output_path):
    """
    Generates a capabilities.json file for the given armature.

    For each bone in the armature, it creates three:
      - Input 'gyro' entries (each with the bone's name + '_RYP').
      - Output 'servo' entries (each with the bone's name).
    
    The indexing is such that for bone 0, the entries are at indices 0, 1, and 2;
    for bone 1, at 3, 4, and 5; and so on.

    Parameters:
        armature_name (str): Name of the armature object in Blender.
        output_path (str): File path where the JSON file will be written.
    """
    armature = bpy.data.objects.get(armature_name)
    if not armature or armature.type != 'ARMATURE':
        print(f"Armature '{armature_name}' not found or is not an armature")
        return

    capabilities = {
        "capabilities": {
            "input": {
                "gyro": {}
            },
            "output": {
                "servo": {}
            }
        }
    }

    gyro_capabilities = {}
    servo_capabilities = {}

    # Iterate over all pose bones in the armature.
    # For each bone, create three entries.
    feagi_index_for_gyro = 0
    for bone_index, bone in enumerate(armature.pose.bones):
        gyro_range = compute_gyro_range(bone)
        servo_range = compute_servo_range(bone)
        for axis in range(3):
            final_index = bone_index * 3 + axis
            
            # Create the output servo capability for this axis of the bone.
            servo_capabilities[str(final_index)] = {
                "custom_name": bone.name,  # same name for each axis.
                "default_value": 0,
                "disabled": False,
                "feagi_index": final_index,
                "max_power": 0.05,
                "max_value": servo_range["max_value"],
                "min_value": servo_range["min_value"]
            }

        # Temp workaround, TODO: Fix Feagi connector on gyro overlapping
        # Create the input gyro capability for this axis of the bone.
        gyro_capabilities[str(bone_index)] = {
            "custom_name": f"{bone.name}_RYP",  # same custom name for each axis.
            "disabled": False,
            "feagi_index": feagi_index_for_gyro,
            "max_value": [gyro_range["max_value"], gyro_range["max_value"], gyro_range["max_value"]],
            "min_value": [gyro_range["min_value"], gyro_range["min_value"], gyro_range["min_value"]]
        }
        feagi_index_for_gyro += 3

    # Insert our generated entries into the capabilities dictionary.
    capabilities["capabilities"]["input"]["gyro"] = gyro_capabilities
    capabilities["capabilities"]["output"]["servo"] = servo_capabilities

    # Write the JSON data to the specified file.
    with open(output_path, "w") as outfile:
        json.dump(capabilities, outfile, indent=4)
    
def main():
    blend_dir = bpy.path.abspath("//")
    json_path = os.path.join(blend_dir, "capabilities.json")
    generate_capabilities_json("ClassicMan_Rigify", json_path)

if __name__ == "__main__":
    main()