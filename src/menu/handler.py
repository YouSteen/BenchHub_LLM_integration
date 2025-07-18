import sys
import os
import msvcrt
from menu.options.send_emails.email_sender import run_email_sender
from menu.options.configuration.configure import configure_options
from menu.options.preview.preview import preview_file
from menu.options.exit.exit import exit_app

# Orange ANSI escape code
ORANGE = "\033[38;2;255;140;0m"
RESET = "\033[0m"

# Endava logo (ASCII art, orange)
endava_logo = f"""
{ORANGE}
        ⬤   
       ⬤ ⬤ 
{RESET}"""

state_of_the_Art = f"""
{ORANGE}                  __                 
  ___  ____  ____/ /___ __   ______ _
 / _ \/ __ \/ __  / __ `/ | / / __ `/     ⬤
/  __/ / / / /_/ / /_/ /| |/ / /_/ /    ⬤ 
\___/_/ /_/\__,_/\__,_/ |___/\__,_/       ⬤ 
{RESET}
                                BenchHub LLM Integration

"""
def main_menu():
    menu_items = [
        "Run Email Sender",
        "Configure Options",
        "Preview File",
        "Exit"
    ]
    selected = 0
    while True:
        # Clear console (Windows)
        if sys.platform.startswith('win'):
            os.system('cls')
        else:
            os.system('clear')
        print(state_of_the_Art)
        print("\nBenchHub LLM Integration Menu:")
        for idx, item in enumerate(menu_items):
            prefix = "-> " if idx == selected else "   "
            print(f"{prefix}{idx+1}. {item}")
        print("\nUse Up/Down arrows to move, Enter to select.")

        key = msvcrt.getch()
        if key == b'\xe0':  # Special keys (arrows, f keys, ins, del, etc.)
            key2 = msvcrt.getch()
            if key2 == b'H':  # Up arrow
                selected = (selected - 1) % len(menu_items)
            elif key2 == b'P':  # Down arrow
                selected = (selected + 1) % len(menu_items)
        elif key == b'\r':  # Enter
            if selected == 0:
                run_email_sender()
            elif selected == 1:
                configure_options()
            elif selected == 2:
                preview_file()
            elif selected == 3:
                exit_app()

if __name__ == "__main__":
    main_menu()
