from pathlib import Path
from .utils import (
    load_survey_df,
    get_unsent_people,
    get_id_name_email,
    display_people_table,
)
from menu.utils.config_manager import load_config, get_config_path
import os


def preview_file():
    from menu.handler import main_menu

    # Check config.ini existence
    config_path = get_config_path()
    if not os.path.exists(config_path):
        print(
            "Error: Configuration not found. Please configure paths from the configuration options menu first."
        )
        input("Press Enter to return to the main menu...")
        return main_menu()

    config = load_config()
    excel_path = config["Paths"].get("survey_path", "")

    # Check Excel path
    if not excel_path or not os.path.exists(excel_path):
        print(
            "Error: Survey Excel file path is not set or file does not exist. Please configure it from the configuration options menu."
        )
        input("Press Enter to return to the main menu...")
        return main_menu()

    df = load_survey_df(excel_path)
    if df is None or df.empty:
        print(
            "Error: Survey Excel file is empty or could not be loaded. Please check the file and configure it from the configuration options menu."
        )
        input("Press Enter to return to the main menu...")
        return main_menu()

    print(f"Loaded: {excel_path}\n")
    filtered = get_unsent_people(df)
    filtered = get_id_name_email(filtered)
    print("\nPeople who have NOT been sent an email:\n")
    display_people_table(filtered)
    input("\nPress Enter to return to the main menu...")
    main_menu()


if __name__ == "__main__":
    preview_file()
