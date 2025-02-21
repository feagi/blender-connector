# blender-connector
Connect FEAGI with Blender to enable embodied AI controlling blender models.

# Quick start
1) git clone git@github.com:feagi/blender-connector.git
2) Drop your blend character into the `blender-connector/controller` folder.  
3) Open Blender.
4) Load the file you dropped into the controller folder.  
5) Click the Scripts tab.
6) Open `controller.py`.  
7) Run the code.

# Install python packages such as feagi_connector
1) Run `lazy_pip.py` (Edit the package name if you want a different package.)

---
## Controller Methods

**`print_armature_info()`** 

 Iteratively prints all non-armature objects in model to the console in the format `Object: object_name`. Prints all armature objects and their bones to the console in the format `Armature: armature_name` and `Bone: bone_name` respectively. \
**Parameters**: none\
**Returns**: None

---

**`validate_connected_bone_movement(armature_name: str, curr_bone_name: str) -> list[Bone]`**

Verify if a rigged bone will affect connected bones when moved. 

- Checks for IK vs FK rigging
- Checks all bones in the armature for copy constraints

**Parameters**\
`armature_name` (str) - The name of the armature that contains the moved bone\
`curr_bone_name` (str) - The name of the bone being moved\
**Returns**: A list of affected bones (including the bone being moved)

---
**`traverse_children(bone: Bone, children_list: list[Bone])`**

Recursively traverses the children of a given bone and appends them to a specified list

**Parameters**\
`bone` (Bone) - the bone to start the traversal from or the root of the desired subtree of Bones\
`children_list` (list[Bone]) - the list all children of the given bone will be appended to\
**Returns**: None

---
**`reset(armature_name: str)`**\
Resets all translations, rotations, and scaling of all bones within the given armature to the following default values:

      - Translation: (0.0, 0.0, 0.0)
      - Rotation: (0.0, 0.0, 0.0)
      - Scale:    (1.0, 1.0, 1.0)
**Parameters**\
`armature_name (str)` - the name of the armature to be reset\
**Returns**: None

---
**`move_bone_in_pose_mode(armature_name: str, bone_name: str, new_location: tuple[x: float, y: float, z: float])`**

Translates a specified bone in pose mode by desired values

**Parameters**\
`armature_name` (str)- name of the armature that contains the bone to be scaled\
`bone_name` (str) - name of the bone to be scaled\
`new_location`(tuple[x: float, y: float, z: float]) - the desired x, y, and z values by which to translate the given bone\
**Returns**: None

---

**`scale_bone_in_pose_mode(armature_name: str, bone_name: str, new_scale: tuple[x: float, y: float, z: float])`**

Scales a specified bone in pose mode by desired values

**Parameters**\
`armature_name` (str)- name of the armature that contains the bone to be scaled\
`bone_name` (str) - name of the bone to be scaled\
`new_scale`(tuple[x: float, y: float, z: float]) - the desired x, y, and z values by which to scale the given bone\
**Returns**: None

---
**`rotate_bone_in_pose_mode(armature_name: str, bone_name: str, new_rotation: tuple[roll: float, pitch: float, yaw: float]`**

Rotates a specified bone in pose mode by desired values

**Parameters**\
`armature_name` (str)- name of the armature that contains the bone to be rotated\
`bone_name` (str) - name of the bone to be rotated\
`new_rotation`(tuple[roll: float, pitch: float, yaw: float]) - the desired roll, pitch, and yaw by which to rotate the given bone, where:

-  **roll** is rotation around the **x-axis**
- **pitch** is rotation around the **y-axis**
- **yaw** is rotation around the **z-axis**

**`new_rotation` Must be provided as Euler angles in radians**.

**Returns**: None

---
**`transform_multiple_bones_in_pose_mode(armature_name: str, bone_transforms: dict, frame: int, keyframe: bool)`**

Transforms multiple bones simultaneously in pose mode. Can specify **translation** and/or **rotation** for each bone provided.

**Parameters**\
`armature_name` (str) - name of the armature objects that contains the bones to be transformed \
`bone_transforms` (dict) - a dictionary where each key is a bone name (str) and its value is another dictionary that can include:

- `"location": tuple[x: float, y: float, z: float]`
- `"rotation": tuple[rx: float, ry: float, rz: float]` where `rx`, `ry`, and `rz` are in **radians**

`frame` (int) - Frame where transform keyframes will be set. \
`keyframe` (bool) - If true sets a keyframe on `frame` for all transformed bones in function. If false keyframe will not be saved.

**Returns**: None