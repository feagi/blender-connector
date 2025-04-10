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
    length = compute_bone_length(bone)
    k = 0.5  # Adjust this constant to scale the dynamic range as needed.
    
    # Avoid division by zero by setting a minimum length value.
    if length < 1e-6:
        dynamic_range = k  # Or some default value.
    else:
        dynamic_range = k / length
        
    return {"max_value": dynamic_range, "min_value": -dynamic_range} 

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

def check_capabilities_ranges(gyro_caps, servo_caps):
    mismatch_found = False
    for gyro_key in gyro_caps:
        bone_index = int(gyro_key)
        servo_key = str(bone_index * 3)
        if servo_key in servo_caps:
            servo_entry = servo_caps[servo_key]
            servo_max_list = [servo_entry["max_value"]] * len(gyro_caps[gyro_key]["max_value"])
            servo_min_list = [servo_entry["min_value"]] * len(gyro_caps[gyro_key]["min_value"])
            if (gyro_caps[gyro_key]["max_value"] != servo_max_list or
                gyro_caps[gyro_key]["min_value"] != servo_min_list):
                print(f"Warning: Mismatch for bone '{gyro_caps[gyro_key]['custom_name']}' (gyro key {gyro_key}):")
                print(f"  Gyro: max {gyro_caps[gyro_key]['max_value']}, min {gyro_caps[gyro_key]['min_value']}")
                print(f"  Servo: max {servo_max_list}, min {servo_min_list}")
                mismatch_found = True
        else:
            print(f"Warning: Servo entry for bone index {bone_index} not found.")
            mismatch_found = True

    if not mismatch_found:
        print("all values match.")

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
        feagi_index_for_gyro = 0
        for bone_index, bone in enumerate(armature.pose.bones):
            gyro_range = compute_gyro_range(bone)
            servo_range = compute_servo_range(bone)
            for axis in range(3):
                final_index = cont_index * 3 + axis
                
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
                    "custom_name": bone.name,  # same custom name for each axis.
                    "disabled": False,
                    "feagi_index": feagi_index_for_gyro,
                    "max_value": [gyro_range["max_value"], gyro_range["max_value"], gyro_range["max_value"]],
                    "min_value": [gyro_range["min_value"], gyro_range["min_value"], gyro_range["min_value"]]
                }
            feagi_index_for_gyro += 3 # temp.....zzz

            cont_index+=1

        check_capabilities_ranges(gyro_capabilities, servo_capabilities)

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