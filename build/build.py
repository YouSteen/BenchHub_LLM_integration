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
    "--noconsole",
    f"--distpath=..",
    f"--workpath=build/temp",
    "../src/main.py",
    "--add-data",
    f"{lib_path}{sep}{target_path}",
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

# Ensure assets/logo.png is included in the build output
src_logo = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
)
dest_dir = os.path.join(os.path.dirname(__file__), "dist", "assets")
os.makedirs(dest_dir, exist_ok=True)
dest_logo = os.path.join(dest_dir, "logo.png")
shutil.copy2(src_logo, dest_logo)
