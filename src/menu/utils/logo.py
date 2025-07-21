import sys
import os

# Orange ANSI escape code
ORANGE = "\033[38;2;255;140;0m"
RESET = "\033[0m"


def get_logo():
    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")
    print(f"""
{ORANGE}                  __                 
  ___  ____  ____/ /___ __   ______ _
 / _ \/ __ \/ __  / __ `/ | / / __ `/     ⬤
/  __/ / / / /_/ / /_/ /| |/ / /_/ /    ⬤ 
\___/_/ /_/\__,_/\__,_/ |___/\__,_/       ⬤ 
{RESET}
                                BenchHub LLM Integration

""")
