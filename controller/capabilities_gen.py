import bpy 
import json
import os


def get_all_armature_names():
    """stores all armature names in list removing duplicates (not yet)"""
    armature_names = []
    metarig_names = []

    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            if "_Rigify" in obj.name:                       # check if armature is Rigify
                
                rig_idx = obj.name.index("_Rigify")         # get index of _Rigify postfix
                metarig_name = obj.name[0:rig_idx]          # get metarig substring
                metarig_names.append(metarig_name)          # add metarig name to metarig list
                armature_names.append(obj.name)             # add rigify name to armature list
            else:
                armature_names.append(obj.name)
        
        for metarig in metarig_names:                       # iterate through list of metarig names
            if metarig in armature_names:                   # remove if in armature list
                armature_names.remove(metarig)
    return armature_names


def generate_capabilities_json(armature_names, output_path):
    """
    Generates a capabilities.json file for the given armatures.

    For each bone in the armature, it creates three:
      - Input 'gyro' entries (each with the bone's name + '_RYP').
      - Output 'servo' entries (each with the bone's name).
    
    The indexing is such that for bone 0, the entries are at indices 0, 1, and 2;
    for bone 1, at 3, 4, and 5; and so on.

    Parameters:
        armature_name (str[]): Names of the armature objects in Blender.
        output_path (str): File path where the JSON file will be written.
    """
    cont_index = 0  # track indices over all armatures 

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

    for armature_name in armature_names:
        armature = bpy.data.objects.get(armature_name)
        print(f"Current armature:{armature_name}")
        if not armature or armature.type != 'ARMATURE':
            print(f"Armature '{armature_name}' not found or is not an armature")
            return

        gyro_capabilities = {}
        servo_capabilities = {}

        # Iterate over all pose bones in the armature.
        # For each bone, create three entries.
        for bone in armature.pose.bones:
            for axis in range(3):
                final_index = cont_index * 3 + axis
                print(final_index)

                # Create the input gyro capability for this axis of the bone.
                gyro_capabilities[str(final_index)] = {
                    "custom_name": f"{bone.name}_RYP",  # same custom name for each axis.
                    "disabled": False,
                    "feagi_index": final_index,
                    "max_value": [0, 0, 0],
                    "min_value": [0, 0, 0]
                }
                
                # Create the output servo capability for this axis of the bone.
                servo_capabilities[str(final_index)] = {
                    "custom_name": bone.name,  # same name for each axis.
                    "default_value": 0,
                    "disabled": False,
                    "feagi_index": final_index,
                    "max_power": 0.05,
                    "max_value": 0.5,
                    "min_value": -0.5
                }

            cont_index+=1   # increment continuous index 

        # Insert our generated entries into the capabilities dictionary.
        capabilities["capabilities"]["input"]["gyro"].update(gyro_capabilities)
        capabilities["capabilities"]["output"]["servo"].update(servo_capabilities)

    # Write the JSON data to the specified file.
    with open(output_path, "w") as outfile:
        json.dump(capabilities, outfile, indent=4)            
    
def main():

    blend_dir = bpy.path.abspath("//")
    json_path = os.path.join(blend_dir, "capabilities.json")

    generate_capabilities_json(get_all_armature_names(), json_path)

if __name__ == "__main__":
    main()