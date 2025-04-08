import bpy
import os
import sys
from mathutils import Vector, Euler

def clear_terminal():
    # Windows uses 'cls', macOS/Linux use 'clear'
    os.system('cls' if os.name == 'nt' else 'clear')


def print_armature_info():
    """Print all objects, highlighting armatures and their bones."""
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            print(f"Armature: {obj.name}")
            for bone in obj.pose.bones:
                print(f"  Bone: {bone.name}")
        else:
            print(f"Object: {obj.name}")

def get_max_translation(armature_name="MyRig", bone_parent_name="StartBone"):
    """To ensure that we don't stretch bones too far, we need to find their max length"""

    if armature_name not in bpy.data.objects:
        print(f"Armature '{armature_name}' not found in bpy.data.objects")
        return

    armature_obj = bpy.data.objects[armature_name]

# 5. Verify if a rigged bone will affect connected bones when moved 
def validate_connected_bone_movement(armature_name="MyRig", curr_bone_name="root"):

    # if IK: any parent bones in IK chain will move
    # if FK: any children will move

    # list of affected bones
    affected_bones = []

    # validate armature name
    if armature_name not in bpy.data.objects:
        print(f"Armature '{armature_name}' not found in bpy.data.objects")
        return

    # get armature object
    armature_obj = bpy.data.objects[armature_name]

    # 3. Switch to Pose Mode
    bpy.ops.object.mode_set(mode='POSE')

    # 4. Check if the bone exists in pose mode
    if curr_bone_name not in armature_obj.pose.bones:
        print(f"Bone '{curr_bone_name}' not found in armature '{armature_name}'")
        return

    # get the bone being moved
    main_bone = armature_obj.pose.bones[curr_bone_name]

    # iterate through that bone's constraints
    for constraint in main_bone.constraints:

        # check if bone has IK constraint
        if constraint.type == 'IK':

            # get number of bones in chain
            chain_num_bones = constraint.chain_count
            print(f"Constraint Name: {constraint.name}, Type: {constraint.type}")
            print(f"chain length: {chain_num_bones}")

            curr_bone = main_bone

            # iterate up IK chain 
            for x in range(chain_num_bones):
                affected_bones.append(curr_bone)  #add bone to affected bones
                curr_bone = curr_bone.parent

        # else if bone has a default FK constraint       
        else:
            affected_bones.append(main_bone)
            traverse_children(main_bone, affected_bones) # recursively add all children to affected bones

    # check for any bones in entire armature that have copy_transformation constraint
    for bone_name, bone in armature_obj.pose.bones.items():

#        print(f"Current bone: {bone_name}")

        # loop through each bone's constraint
        for constraint in bone.constraints:

            # check if that bone has a copy constraint
            if constraint.type == ('COPY_TRANSFORMS'or 'COPY_LOCATION' or 'COPY_ROTATION' or 'COPY_SCALE'):

                # if the subtarget is the bone we are adjusting
                if main_bone.name == constraint.subtarget:

#                    print(f"{main_bone.name} is the target of {bone.name}")
                    affected_bones.append(bone)

    return affected_bones

# traverse children of a specified bone          
def traverse_children(bone, children_list):

    # base case: at leaf
    if len(bone.children) > 0:
        for child in bone.children:
            children_list.append(child) 
            traverse_children(child, children_list)  


def reset(armature_name="MyRig"):
    """
    Resets the translations, rotations, and scales of all bones
    
    Defaults:
      - location: (0.0, 0.0, 0.0)
      - rotation: (0.0, 0.0, 0.0)
      - scale:    (1.0, 1.0, 1.0)
    """
    if armature_name not in bpy.data.objects:
        print(f"Armature '{armature_name}' not found in bpy.data.objects")
        return

    armature_obj = bpy.data.objects[armature_name]
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')

    for bone_name, bone in armature_obj.pose.bones.items():
        # Reset location to (0.0, 0.0, 0.0)
        bone.location = (0.0, 0.0, 0.0)
        # Reset rotation.
        if bone.rotation_mode in {'XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'}:
            bone.rotation_euler = (0.0, 0.0, 0.0)
        # Reset scale to (1.0, 1.0, 1.0)
        bone.scale = (1.0, 1.0, 1.0)

        print(f"Bone '{bone_name}' reset: location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)")

    bpy.ops.object.mode_set(mode='OBJECT')

def translate_bone(armature_name="MyRig", bone_name="root", new_location=(None, None, None)):
    """
    Moves a specified bone in pose mode.
    If any element in `new_location` is None, the current location value is retained for that axis.
    """
    if armature_name not in bpy.data.objects:
        print(f"Armature '{armature_name}' not found in bpy.data.objects")
        return

    armature_obj = bpy.data.objects[armature_name]
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')

    if bone_name not in armature_obj.pose.bones:
        print(f"Bone '{bone_name}' not found in armature '{armature_name}'")
        return

    bone = armature_obj.pose.bones[bone_name]

    # Get current location as a vector
    current_location = bone.location.copy()
    new_x, new_y, new_z = new_location

    # Update only if a new value is provided
    if new_x is not None:
        current_location.x = new_x
    if new_y is not None:
        current_location.y = new_y
    if new_z is not None:
        current_location.z = new_z

    bone.location = current_location
    print(f"Bone '{bone_name}' in '{armature_name}' moved to {bone.location}")

    bpy.ops.object.mode_set(mode='OBJECT')

def scale_bone(armature_name="MyRig", bone_name="root", new_scale=(None, None, None)):
    """
    Scales a specified bone in pose mode.
    If any element in `new_scale` is None, the current scale value is retained for that axis.
    """
    if armature_name not in bpy.data.objects:
        print(f"Armature '{armature_name}' not found in bpy.data.objects")
        return

    armature_obj = bpy.data.objects[armature_name]
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')

    if bone_name not in armature_obj.pose.bones:
        print(f"Bone '{bone_name}' not found in armature '{armature_name}'")
        return

    bone = armature_obj.pose.bones[bone_name]

    # Get current scale as a mutable vector
    current_scale = bone.scale.copy()
    new_x, new_y, new_z = new_scale

    # Update only if a new value is provided
    if new_x is not None:
        current_scale.x = new_x
    if new_y is not None:
        current_scale.y = new_y
    if new_z is not None:
        current_scale.z = new_z

    bone.scale = current_scale
    print(f"Bone '{bone_name}' in '{armature_name}' scaled to {bone.scale}")

    bpy.ops.object.mode_set(mode='OBJECT')

def transform_multiple_bones_in_pose_mode(armature_name="MyRig", bone_transforms=None, frame=None, keyframe=True):
    """
    Transforms multiple bones simultaneously in pose mode.
    For each bone provided, you can specify a new location and/or a new rotation.
    
    Parameters:
        armature_name (str): Name of the armature object.
        bone_transforms (dict): A dictionary where each key is a bone name (str) and its
                                value is another dictionary that can include:
                                  - "location": A tuple (x, y, z)
                                  - "rotation": A tuple (rx, ry, rz) in radians
    """
    if bone_transforms is None:
        print("No bone transforms provided.")
        return

    if armature_name not in bpy.data.objects:
        print(f"Armature '{armature_name}' not found in bpy.data.objects")
        return

    armature_obj = bpy.data.objects[armature_name]
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')

    if frame is not None:
        bpy.context.scene.frame_set(frame)

    for bone_name, transforms in bone_transforms.items():
        if bone_name not in armature_obj.pose.bones:
            print(f"Bone '{bone_name}' not found in armature '{armature_name}'")
            continue

        bone = armature_obj.pose.bones[bone_name]
        
        # Update translation if provided
        if "location" in transforms:
            bone.location = transforms["location"]
            if keyframe:
                bone.keyframe_insert(data_path="location", index=-1)
            print(f"Bone '{bone_name}' moved to {transforms['location']}")
        
        # Update rotation if provided
        if "rotation" in transforms:
            bone.rotation_mode = 'XYZ'  # Ensure we are using Euler rotations
            bone.rotation_euler = transforms["rotation"]
            if keyframe:
                bone.keyframe_insert(data_path="rotation_euler", index=-1)
            print(f"Bone '{bone_name}' rotated to {transforms['rotation']}")

    if frame is not None:
        marker_name = f"Keyframe {frame}"
        bpy.context.scene.timeline_markers.new(marker_name, frame=frame)


    bpy.ops.object.mode_set(mode='OBJECT')

def change_ryp(armature_name="MyRig", bone_name="root", new_ryp=None):
    """
    Changes the rotation of a specified bone in pose mode using roll, yaw, and pitch values.
    This version allows partial updates (e.g., only roll, or only yaw, etc.).

    Assumptions:
      - The bone's rotation mode is set to 'XYZ'.
      - The tuple new_ryp = (roll, yaw, pitch).
      - If any element in new_ryp is None, that axis is left unchanged.

    Parameters:
        armature_name (str): Name of the armature object.
        bone_name (str): Name of the bone to be rotated.
        new_ryp (tuple): A tuple of three floats (or None) representing (roll, yaw, pitch).
    """
    # Check if the armature exists
    if new_ryp is None:
        new_ryp = [None, None, None]
    if armature_name not in bpy.data.objects:
        print(f"Armature '{armature_name}' not found in bpy.data.objects")
        return

    armature_obj = bpy.data.objects[armature_name]
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')

    # Check if the bone exists in pose mode
    if bone_name not in armature_obj.pose.bones:
        print(f"Bone '{bone_name}' not found in armature '{armature_name}'")
        bpy.ops.object.mode_set(mode='OBJECT')
        return

    bone = armature_obj.pose.bones[bone_name]

    # Ensure rotation mode is 'XYZ'
    bone.rotation_mode = 'XYZ'

    # Get the current rotation
    current_euler = bone.rotation_euler.copy()

    # Unpack the new roll, yaw, pitch
    roll, yaw, pitch = new_ryp

    # If any component is None, keep the current value
    if roll is not None:
        current_euler.x = roll
    if yaw is not None:
        current_euler.y = yaw
    if pitch is not None:
        current_euler.z = pitch

    # Assign the updated rotation back to the bone
    bone.rotation_euler = current_euler
    
    # Return to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')

def get_property_type(data_path):
#takes data path to return string of keyframe type
    if "location" in data_path:
        return "Location"
    elif "scale" in data_path:
        return "Scale"
    elif "rotation_quaternion" in data_path:
        return "Rotation (Quaternion)"
    elif "rotation_euler" in data_path:
        return "Rotation (Euler)"
    else:
        return "Other"

def keyframe_selected_bones(armature_name = "MyRig",current_frame = 0):
    armature = bpy.data.objects.get(armature_name)

    if not armature:
        print(f"Armature '{armature}' not found.")
        return

    if armature.type != 'ARMATURE':
        print(f"'{armature}' is not an armature.")
        return
    
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    pose_bones = armature.pose.bones

    for bone in pose_bones:
        if bone.bone.select:
            bone.keyframe_insert(data_path="location", frame=current_frame)
            bone.keyframe_insert(data_path="rotation_euler", frame=current_frame)
            bone.keyframe_insert(data_path="scale", frame=current_frame)
    marker_name = f"Keyframe {current_frame}"
    bpy.context.scene.timeline_markers.new(marker_name, frame=current_frame)


def keyframe_full_armature(armature_name = "MyRig",current_frame = 0):
    armature = bpy.data.objects.get(armature_name)

    if not armature:
        print(f"Armature '{armature}' not found.")
        return

    if armature.type != 'ARMATURE':
        print(f"'{armature}' is not an armature.")
        return

    pose_bones = armature.pose.bones

    for bone in pose_bones:
        bone.keyframe_insert(data_path="location", frame=current_frame)
        bone.keyframe_insert(data_path="rotation_euler", frame=current_frame)
        bone.keyframe_insert(data_path="scale", frame=current_frame)
    marker_name = f"Keyframe {current_frame}"
    bpy.context.scene.timeline_markers.new(marker_name, frame=current_frame)

def print_all_keyframes():
    for obj in bpy.context.scene.objects:
        keyframe_dict = {}
        if obj.type == 'ARMATURE' and obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            for fcurve in action.fcurves:
                data_path = fcurve.data_path
                bone_name = data_path.split('"')[1] if '"' in data_path else "unknown"
                property_type = get_property_type(data_path)
            
                if bone_name not in keyframe_dict:
                    keyframe_dict[bone_name] = {}
            
                if property_type not in keyframe_dict[bone_name]:
                    keyframe_dict[bone_name][property_type] = set()

                for keyframe in fcurve.keyframe_points:
                    keyframe_dict[bone_name][property_type].add(int(keyframe.co.x))

        for bone, prop_dict in keyframe_dict.items():
            print(f"Bone: {bone}")
            for prop_type, frames in prop_dict.items():
                print(f"  {prop_type}: {sorted(frames)}")
    print("Printed all Keyframes.")

def clear_armature_keyframe(armature_name = "MyRig"):
    obj = bpy.data.objects.get(armature_name)

    if not obj:
        print(f"Object '{armature_name}' not found.")
        return

    if obj.animation_data:
        action = obj.animation_data.action
        if action:
            print(f"Clearing keyframes and unlinking action from '{armature_name}'...")

            # Clear fcurves (animation data)
            action.fcurves.clear()

            # Unlink the action
            obj.animation_data.action = None

def clear_all_keyframes():
    for obj in bpy.context.scene.objects:
        if obj.animation_data:
            action = obj.animation_data.action
            if action:
                # Clear fcurves (animation data)
                action.fcurves.clear()

                # Unlink the action
                obj.animation_data.action = None
    print("Cleared all Armatures")

def reset_armature(armature_name = "MyRig"):
    obj = bpy.data.objects.get(armature_name)

    if obj and obj.type == 'ARMATURE':
        bpy.context.view_layer.objects.active = obj  # make it active
        bpy.ops.object.mode_set(mode='POSE')         # switch to Pose Mode
        bpy.ops.pose.select_all(action='SELECT')     # select all bones
        bpy.ops.pose.transforms_clear()       # clear location, rotation, and scale
        print(f"Pose reset to rest position for '{armature_name}'.")
    else:
        print("Armature not found")

def print_keyframe(current_frame = 0):
    bpy.context.scene.frame_set(current_frame)

    for obj in bpy.context.scene.objects:
        if obj.type != 'ARMATURE' or not obj.animation_data or not obj.animation_data.action:
            continue

        action = obj.animation_data.action
        keyed_bones = {}

        for fcurve in action.fcurves:
            data_path = fcurve.data_path
            property_type = get_property_type(data_path)

            if not property_type or '"' not in data_path:
                continue

            bone_name = data_path.split('"')[1]

            for kf in fcurve.keyframe_points:
                if int(kf.co.x) == current_frame:
                    if bone_name not in keyed_bones:
                        keyed_bones[bone_name] = set()
                    keyed_bones[bone_name].add(property_type)

        if keyed_bones:
            print(f"\nArmature: {obj.name} \nAt keyframe on frame: {current_frame}")
            for bone_name in keyed_bones:
                bone = obj.pose.bones.get(bone_name)
                if not bone:
                    continue

                loc = bone.location
                rot = bone.rotation_euler
                scl = bone.scale

                print(f"  Bone: {bone.name}")
                print(f"    Location: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f})")
                print(f"    Rotation (Euler): ({rot.x:.3f}, {rot.y:.3f}, {rot.z:.3f})")
                print(f"    Scale: ({scl.x:.3f}, {scl.y:.3f}, {scl.z:.3f})")

def get_keyed_bones(current_frame = 0):
    bpy.context.scene.frame_set(current_frame)
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.type != 'ARMATURE' or not obj.animation_data or not obj.animation_data.action:
            continue

        action = obj.animation_data.action
        keyed_bones = {}

        for fcurve in action.fcurves:
            data_path = fcurve.data_path
            property_type = get_property_type(data_path)

            if not property_type or '"' not in data_path:
                continue

            bone_name = data_path.split('"')[1]

            pose_bone = obj.pose.bones.get(bone_name)

            for kf in fcurve.keyframe_points:
                if int(kf.co.x) == current_frame:
                    properties = set()
                    if pose_bone.location != Vector((0,0,0)):
                        properties.add("location")
                    if pose_bone.rotation_euler != Euler((0,0,0)):
                        if any(abs(a - b) > 1e-4 for a, b in zip(pose_bone.rotation_euler, Euler((0, 0, 0), pose_bone.rotation_mode))):
                            properties.add("rotation_euler")
                    if pose_bone.scale != Vector((1,1,1)):
                        properties.add("scale")
                    
                    if properties:
                        if bone_name not in keyed_bones:
                            keyed_bones[bone_name] = set()
                        keyed_bones[bone_name].update(properties)


        if keyed_bones:
            print(f"\nArmature: {obj.name}")
            for bone, props in keyed_bones.items():
                print(f"  Bone: {bone}")
                print(f"    Keyed: {', '.join(sorted(props))}")
            result.update(keyed_bones)

        return result



def main():

    clear_terminal()
    # clear_armature_keyframe("ClassicMan_Rigify")
    # print_all_keyframes()
    # reset_armature()
    # keyframe_full_armature("ClassicMan_Rigify",1)
    # keyframe_selected_bones("ClassicMan_Rigify",20)
    # print_keyframe(20)
    # print_all_keyframes()
    # bones = get_keyed_bones(20)
    # print("\nReturned list of keyed bones:", bones)


    # print(sys.executable)

    # 1. Print available armatures and bones so you can see the exact names
    #print_armature_info()

    # translate entire body
    # move_bone_in_pose_mode("ClassicMan_Rigify", "root", (0.0, 0.0, 0.0))

    # 2. translate
    # move_bone_in_pose_mode("ClassicMan_Rigify", "hand_ik.R", (0.0, 0.0, 0.0))
    # move_bone_in_pose_mode("ClassicMan_Rigify", "upper_arm_ik.R", (0.0, 0.0, 0.0))
    # move_bone_in_pose_mode("ClassicMan_Rigify", "hand_ik.L", (0.0, 0.0, 0.0))
    # move_bone_in_pose_mode("ClassicMan_Rigify", "thigh_ik.L", (0.0, 0.0, 0.0))
    # move_bone_in_pose_mode("ClassicMan_Rigify", "thigh_ik.R", (-0.0, 0.0, 0.0))
    # move_bone_in_pose_mode("ClassicMan_Rigify", "foot_ik.L", (-0.0, 0.0, 0.0))
    # move_bone_in_pose_mode("ClassicMan_Rigify", "ring.01.L", (-0.0, 0.0, 0.0))

    # 3.scale
    # scale_bone_in_pose_mode("ClassicMan_Rigify", "root", (2.0, 2.0, 2.0))
    # scale_bone_in_pose_mode("ClassicMan_Rigify", "thumb.01.L", (1.0, 1.0, 1.0))
    # scale_bone_in_pose_mode("ClassicMan_Rigify", "torso", (1.0, 1.0, 1.0))
    # scale_bone_in_pose_mode("ClassicMan_Rigify", "foot_ik.L", (1.0, 1.0, 1.0))


    #4.rotation
    # change_ryp("ClassicMan_Rigify", "root", (None, 1.0, 2.0))
    # change_ryp("ClassicMan_Rigify", "hand_ik.R", (1.5, None, 1.1))
    # change_ryp("ClassicMan_Rigify", "torso", (None, 3.0, None))
    # change_ryp("ClassicMan_Rigify", "palm.L", (2.0, None, 2.0))

    #5. moves multiple bones
    # bone_transforms = {
    #     "hand_ik.R": {"location": (0.5, 0.0, 0.0), "rotation": (0.0, 2.0, 0.0)},
    #     "upper_arm_ik.R": {"location": (0.0, 0.0, 0.0)},
    #     "foot_ik.L": {"location": (0.0, -0.0, 0.5)},
    #     "thigh_ik.L": {"location": (0.0, -0.1, 0.0), "rotation": (0.1, 0.0, 0.0)},
    #     "thigh_ik.R": {"location": (0.0, 0.0, 0.1)}
    # }
    
    # transform_multiple_bones_in_pose_mode("ClassicMan_Rigify", bone_transforms, 1 , True)

    # bone_transforms = {
    #     "hand_ik.R": {"location": (0.5, 0.0, 0.0), "rotation": (0.0, 2.3, 0.0)},
    #     "upper_arm_ik.R": {"location": (0.0, 0.0, 0.0)},
    #     "foot_ik.L": {"location": (0.0, -0.4, 0.5)},
    #     "thigh_ik.L": {"location": (0.0, 0.1, 0.0), "rotation": (-0.1, 0.4, 0.0)},
    #     "thigh_ik.R": {"location": (0.0, 0.0, -0.1)}
    # }
    
    # transform_multiple_bones_in_pose_mode("ClassicMan_Rigify", bone_transforms, 20 , True)

    # #6. reset bone tranformations
    # # reset("ClassicMan_Rigify")
    # # get_bones_with_IK("ClassicMan_Rigify")
    # affected_bones = validate_connected_bone_movement(armature="ClassicMan_Rigify", curr_bone_name="")
    # for bone in affected_bones:
    #     print(bone)

# Entry point
if __name__ == "__main__":
    main()