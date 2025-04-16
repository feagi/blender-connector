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

# Run Blender Character on NeuroRobotics Studio  
1) Clone the repository: `git clone git@github.com:feagi/blender-connector.git`  
2) Drop your .blend character into the `blender-connector/controller` folder.  
3) Open File Explorer and paste the following path into the address bar: `C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\lib\site-packages\feagi_connector` (You must run `lazy_pop.py` once per installed Blender.)  
4) Click on the address bar, type `cmd`, and press Enter to open the Command Prompt.  
5) Copy and paste the command: `notepad .env`, then click Yes to create the file.  
6) Go to the NeuroRobotics Studio experiment.  
7) Click "Embodiment," then click the "API_KEY" button and paste it into the notepad file. Save the file.  
8) Run `controller.py` inside Blender.

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

# FEAGI Blender Capabilities Generator

This provides a way for Blender that automatically generates a `capabilities.json` file to map Blender armatures (bones) into sensor (`gyro`) and actuator (`servo`) entries for the FEAGI AI framework.

---

## Overview

- **Automated JSON Generation**: Iterates through every bone in all detected armatures, automatically assigning each bone to either servo or gyro entries in the final configuration.
- **Dynamic Range Computation**: Uses a function to compute bone length and derive min/max values for both servo and gyro capabilities.
- **Multi-Armature Support**: If your Blender file contains multiple armatures, each one will be processed and merged into the same `capabilities.json`.
- **Integrity Checks**: A built-in validation step (`check_capabilities_ranges`) ensures consistency between gyro and servo ranges, alerting you if entries do not match.

---

## Features

1. **Per-Bone Gyro Assignment**  
   - Only one gyro entry is created per bone, enabling sensors for real-time feedback in the FEAGI environment.

2. **Per-Bone Servo Group**  
   - Each bone receives three servo entries (one per axis), allowing granular motion control through FEAGI.

3. **Automatic Indexing**  
   - A global index (`cont_index`) increments for each bone, ensuring unique indices across multiple armatures.
   - Gyro entries use the bone index as a key, while servo entries use `cont_index * 3 + axis`.

4. **Range Checking**  
   - After generating capabilities for each armature, the script runs `check_capabilities_ranges` to confirm that your gyro’s range aligns with at least one servo index (the first servo entry for each bone).

---

## Installation & Setup

1. **Open Blender** and load your `.blend` file.
2. **Load** the script (`capabilities_gen.py`) into Blender’s Text Editor.
---

## Usage

1. **Run the Script**  
   - In Blender’s Text Editor, press **Run Script**.
2. **Output File**  
   - The script writes a `capabilities.json` file to the same directory as your `.blend` file.  
3. **Inspect Logs**  
   - Check Blender’s console for any **mismatch** warnings or errors during range checks.

---

## Key Functions

- **`compute_bone_length(bone)`**  
  Calculates a bone’s length using the difference between its head and tail coordinates.

- **`compute_gyro_range(bone)`**  
  Returns a dictionary with `"max_value"` and `"min_value"` for the bone’s gyro, often calculated from the bone’s length.

- **`compute_servo_range(bone)`**  
  Similar to `compute_gyro_range`, but can be replaced with a fixed range if desired.

- **`get_all_armature_names()`**  
  Identifies all armatures in the scene, filtering out certain “metarig” entries if you’re using Rigify.

- **`check_capabilities_ranges(gyro_caps, servo_caps)`**  
  Compares each bone’s gyro data with its first servo entry (`bone_index * 3`), reporting mismatches.

- **`generate_capabilities_json(armature_names, output_path)`**  
  The main function. Iterates over each armature and every bone to populate servo and gyro data into the final `capabilities.json`.

---

## Indexing Scheme

- **Gyro Entries**  
  - One gyro entry per bone.  
  - Key: `str(bone_index)` (resets per armature in the local dictionary, then merged into the global JSON).  

- **Servo Entries**  
  - Three servo entries per bone (one for each axis).  
  - Keys: `str(cont_index * 3 + axis)`, where `cont_index` is incremented after each bone, ensuring unique servo indices across all armatures.

---

## Example Flow

1. **Detect Armatures**  
   - `get_all_armature_names()` collects the names.  
2. **Loop Through Bones**  
   - For each bone, compute its ranges using `compute_bone_length` → `compute_gyro_range` and `compute_servo_range`.  
   - Write one gyro entry, three servo entries.  
3. **Check Ranges**  
   - For each bone, compare the first servo entry’s range to the gyro range.  
   - Print a warning if they differ.  
4. **Write JSON**  
   - Merge all local armature dictionaries into one `capabilities.json`.

---