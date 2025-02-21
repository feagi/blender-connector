import subprocess
import sys

python_executable = sys.executable
subprocess.call([python_executable, "-m", "ensurepip"])
subprocess.call([
    python_executable, 
    "-m", 
    "pip", 
    "install",
    "--ignore-installed",
    "--no-user",
    "feagi_connector"
]) #idc

