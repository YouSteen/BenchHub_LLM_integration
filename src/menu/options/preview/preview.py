import os
import sys
import pandas as pd
from tabulate import tabulate

# Helper to clear the terminal
clear_cmd = 'cls' if sys.platform.startswith('win') else 'clear'
def clear_terminal():
    os.system(clear_cmd)

# Helper to find the Excel file in user's home/OneDrive
from pathlib import Path
def find_excel_file():
    home = Path.home()
    for root, dirs, files in os.walk(home):
        for file in files:
            if file.lower().startswith('benchhub_engagement') and file.lower().endswith('.xlsx'):
                return os.path.join(root, file)
    return None

def show_where_left_off():
    print("[Stub] Show where you left off sending emails.")
    input("Press Enter to return to the preview menu...")

def show_missed():
    print("[Stub] Show if there is someone you missed.")
    input("Press Enter to return to the preview menu...")

def show_excel_file():
    clear_terminal()
    excel_path = find_excel_file()
    if not excel_path:
        print("Excel file not found in your home/OneDrive folders.")
        input("Press Enter to return to the preview menu...")
        return
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        input("Press Enter to return to the preview menu...")
        return
    print(f"Loaded: {excel_path}\n")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    print("\nDo you want to show the whole file or a range of lines?")
    print("1. Whole file\n2. Range of lines")
    choice = input("Select option: ").strip()
    if choice == '2':
        start = input("Start row (1-based): ").strip()
        end = input("End row (inclusive): ").strip()
        try:
            start = int(start) - 1
            end = int(end)
            df = df.iloc[start:end]
        except Exception:
            print("Invalid range. Showing whole file.")
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
    input("\nPress Enter to return to the preview menu...")

def preview_file():
    while True:
        clear_terminal()
        print("BenchHub Survey Preview Menu:\n")
        print("1. Show where you left off sending emails")
        print("2. Show if there is someone you missed")
        print("3. Show the whole file or a range of lines")
        print("4. Return to main menu")
        choice = input("Select option: ").strip()
        if choice == '1':
            show_where_left_off()
        elif choice == '2':
            show_missed()
        elif choice == '3':
            show_excel_file()
        elif choice == '4':
            break
        else:
            print("Invalid option. Try again.")
            input("Press Enter to continue...")
