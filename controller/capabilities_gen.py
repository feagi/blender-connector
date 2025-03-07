import bpy 
import json
import os 

def generate_capabilities_json(armature_name, output_path):
    """
    Generates a capabilities.json file for the given armature.
    
    For each bone in the armature, it creates:
      - An input 'gyro' entry using the bone's name with a suffix (e.g., '_RYP').
      - An output 'servo' entry using the bone's name.
    
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
    # Each bone is assigned an index which will serve as its feagi_index.
    for idx, bone in enumerate(armature.pose.bones):
        # Create the input gyro capability for the bone.
        gyro_capabilities[str(idx)] = {
            "custom_name": f"{bone.name}_RYP",  # change naming as needed.
            "disabled": False,
            "feagi_index": idx,
            "max_value": [0, 0, 0],
            "min_value": [0, 0, 0]
        }
        
        # Create the output servo capability for the bone.
        servo_capabilities[str(idx)] = {
            "custom_name": bone.name,
            "default_value": 0,
            "disabled": False,
            "feagi_index": idx,
            "max_power": 0.05,  # adjust these values as needed.
            "max_value": 0.5,
            "min_value": -0.5
        }

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