#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2016-present Neuraville Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================
"""
import os
import bpy
import threading
import sys
from time import sleep
from feagi_connector import sensors
from feagi_connector import actuators
from feagi_connector import retina as retina
from feagi_connector import pns_gateway as pns
from feagi_connector.version import __version__
from feagi_connector import feagi_interface as feagi
from dotenv import load_dotenv

# Get the directory of the current file (assuming .env is in the same directory)
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, ".env")

# Load the .env file from the specified path
load_dotenv(dotenv_path)

# Get the RUN_ENV variable from the environment, defaulting to "local" if not set
run_env = os.getenv("RUN_ENV", "local")

# Option 2: Decide the FEAGI_OPU_PORT based on RUN_ENV
if run_env == "docker":
    feagi_opu_port = "30000"
else:
    feagi_opu_port = "3000"

# Optionally, override the value from the .env file
# Or if you want to update the environment with this value:
os.environ["FEAGI_OPU_PORT"] = feagi_opu_port

print("RUN_ENV:", run_env)
print("Using FEAGI_OPU_PORT:", feagi_opu_port)


# Global variable section
camera_data = {"vision": []}  # This will be heavily rely for vision
map_translation = {0: "head"}  # An example. We need to find a way to scale this


def xyz_to_bone(data_position):
    return data_position // 3


def verify_which_xyz(number):
    fractional_part = number - int(number)
    if fractional_part == 0:
        return 0 # x
    elif abs(fractional_part - 0.33) < 0.01:
        return 1 # y
    elif abs(fractional_part - 0.66) < 0.01:
        return 2 # z
    else:
        return None


def feagi_index_to_bone(feagi_index):
    if feagi_index in map_translation:
        return map_translation[feagi_index]
    else:
        return None


def action(obtained_data):
    """
    This is where you can make the robot do something based on FEAGI data. The variable
    obtained_data contains the data from FEAGI. The variable capabilities comes from
    the configuration.json file. It will need the capability to measure how much power it can control
    and calculate using the FEAGI data.

    obtained_data: dictionary.
    capabilities: dictionary.
    """
    # recieve_motor_data = actuators.get_motor_data(obtained_data)
    # recieve_servo_data = actuators.get_servo_data(obtained_data)
    recieve_servo_position_data = actuators.get_servo_position_data(obtained_data)

    if recieve_servo_position_data:
        # pass # output like {0:0.50, 1:0.20, 2:0.30} # example but the data comes from your capabilities' servo range
        for feagi_index in recieve_servo_position_data:
            movement_data = [None, None, None]  # initialize the ryp. If the index is none, it should be skipped.
            movement_data[verify_which_xyz(feagi_index / 3)] = recieve_servo_position_data[feagi_index] # will update which index from FEAGI
            bone_name = feagi_index_to_bone(xyz_to_bone(feagi_index))
            if bone_name is not None:
                starter.change_ryp("ClassicMan_Rigify", bone_name, movement_data)
    # if recieve_servo_data:
    #     pass  # example output: {0: 0.245, 2: 1.0}
    #
    # if recieve_motor_data:  # example output: {0: 0.245, 2: 1.0}
    #     pass

if __name__ == "__main__":
    # Generate runtime dictionary
    runtime_data = {}

    # This function will build the capabilities from your configuration.json and read the
    # args input. First, it will gather all details from your configuration.json. Once it's done,
    # it will read all input args, such as flags. Once it detects flags from the user, it will override
    # the configuration and use the input provided by the user.

    # blender custom code
    # if len(sys.argv) == 0:
    #     sys.argv = ['blender']  # Add a dummy program name
    if bpy.context.space_data and bpy.context.space_data.type == 'TEXT_EDITOR':  # yep, I was right.
        current_dir = bpy.path.abspath("//")
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:  # Blender trolls
        sys.path.append(current_dir)

        import starter  # if you restart the controller, it will cause an exception.
    # blender custom code

    config = feagi.build_up_from_configuration(current_dir)
    feagi_settings = config['feagi_settings'].copy()
    agent_settings = config['agent_settings'].copy()
    default_capabilities = config['default_capabilities'].copy()
    message_to_feagi = config['message_to_feagi'].copy()
    capabilities = config['capabilities'].copy()

    # Simply copying and pasting the code below will do the full work for you. It basically checks
    # and updates the network to ensure that it can connect with FEAGI. If it doesn't find FEAGI,
    # it will just wait and display "waiting on FEAGI...".
    # # # FEAGI registration # # # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    feagi_settings, runtime_data, api_address, feagi_ipu_channel, feagi_opu_channel = \
        feagi.connect_to_feagi(feagi_settings, runtime_data, agent_settings, capabilities,
                               __version__)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # The function `create_runtime_default_list` will design and generate a complete JSON object
    # in the configuration, mainly for vision only. Once it's done, it will get the configuration JSON,
    # override all keys generated by this function, and store them into the same capabilities for
    # the rest of controller runtime.
    default_capabilities = pns.create_runtime_default_list(default_capabilities, capabilities)

    # This is for processing the data and updating in real-time based on the user's activity in BV,
    # such as cortical size, blink, reload genome, and other backend tasks.
    if capabilities:
        if "camera" in capabilities['input']:
            threading.Thread(target=retina.vision_progress,
                             args=(default_capabilities, feagi_settings, camera_data['vision'],),
                             daemon=True).start()

    for x in capabilities['output']['servo']:
        feagi_index = x
        feagi_index_int = int(x)
        map_translation[feagi_index_int] = capabilities['output']['servo'][feagi_index]['custom_name']


    def gather_gyro_data(armature):
        gyro_data = {}
        for idx, bone in enumerate(armature.pose.bones):
            location_values = [bone.location[0], bone.location[1], bone.location[2]]  # Full (x, y, z) location
            rotation_values = [bone.rotation_euler[0], bone.rotation_euler[1], bone.rotation_euler[2]]  # Full (x, y, z) rotation
            scale_values    = [bone.scale[0], bone.scale[1], bone.scale[2]]  # Full (x, y, z) scale

            # Create a dictionary with keys "0", "1", and "2"
            bone_data = {
                "0":location_values,
                "1":rotation_values,
                "2":scale_values
            }
            
            # Assign this dictionary to the bone's index key (as a string)
            gyro_data[str(idx)] = bone_data
        return gyro_data
    

    def feagi_update():
        # The controller will grab the data from FEAGI in real-time
        message_from_feagi = pns.message_from_feagi
        if message_from_feagi:  # Verify if the feagi data is not empty
            # Translate from feagi data to human readable data
            pns.check_genome_status_no_vision(message_from_feagi)
            obtained_signals = pns.obtain_opu_data(message_from_feagi)
            action(obtained_signals)

        armature = bpy.data.objects.get("ClassicMan_Rigify")
        if armature is None:
            return feagi_settings['feagi_burst_speed']
        
        gyro_data = gather_gyro_data(armature)

        print("Data being sent to FEAGI (first 3 indexes):")
        for idx, (key, value) in enumerate(gyro_data.items()):
            if idx >= 3:
                break
            print(f"Index {key}: {value}")

        # the data should be "{'0': [x,y,z]} taken care of from gather_gyro_data"
        message_to_feagi_local = sensors.create_data_for_feagi('gyro', capabilities, message_to_feagi,
                                                                current_data=gyro_data, symmetric=True)
        # Sends to feagi data
        pns.signals_to_feagi(message_to_feagi_local, feagi_ipu_channel, agent_settings, feagi_settings)

        # Clear data that is created by controller such as sensors
        message_to_feagi.clear()

        # cool down everytime
        return feagi_settings['feagi_burst_speed']

    # Register the timer callback so that it runs periodically without freezing Blender
    bpy.app.timers.register(feagi_update)
