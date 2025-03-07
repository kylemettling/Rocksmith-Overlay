import subprocess
import os

def launch_scripts():
    overlay_process = subprocess.Popen(["python", "overlay.py"])
    overlay_process.wait()

if __name__ == "__main__":
    launch_scripts()