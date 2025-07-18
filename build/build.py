from distutils.sysconfig import get_python_lib
import subprocess
from pathlib import Path
import os
import shutil

site_packages = get_python_lib()
lib_path = Path(site_packages) / "llama_cpp" / "lib"
target_path = "llama_cpp/lib"

if not lib_path.exists():
    raise FileNotFoundError(f"ERROR:Cannot find llama_cpp lib folder at {lib_path}")

sep = ";" if os.name == "nt" else ":"

cmd = [
    "pyinstaller",
    "--name=BenchHubLLM",
    "--onefile",
    "--clean",
    "--log-level=WARN",
    f"--distpath=..",
    f"--workpath=build/temp",
    "../src/main.py",
    "--add-data",
    f"{lib_path}{sep}{target_path}",
    "--add-data",
    f"../assets/logo.png{sep}assets",
]

print(f"""
      =================================
      Running PyInstaller with command: {' '.join(cmd)}
      =================================
      """)
print(" ")
subprocess.run(cmd)
print("""
     ============================== 
      Code successfully compiled.
     ==============================
      """)
