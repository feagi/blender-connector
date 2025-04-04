import bpy
import os
import sys

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

def main():
    
    clear_terminal()
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
    # affected_bones = validate_connected_bone_movement(armature_name="ClassicMan_Rigify", curr_bone_name="")
    # for bone in affected_bones:
    #     print(bone)

# Entry point
if __name__ == "__main__":
    main()
