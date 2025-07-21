from pathlib import Path
from .utils import (
    load_survey_df,
    get_unsent_people,
    get_id_name_email,
    display_people_table,
)
from menu.utils.config_manager import load_config, get_config_path
import os

REQUIRED_COLUMNS = [
    "Id",
    "Start time",
    "Completion time",
    "Email",
    "Name",
    "Please choose the office location you are assigned to.\n",
    "Please provide your Career Coach's email address in the space below.\n",
    "Which areas of upskilling are you most interested in? (You can select multiple options)\n",
    "Are you currently engaged in any training, certifications, or testing activities?\n",
    "If yes, please specify the type of training or certification you're currently engaged with.\n",
    "Are there any specific topics or skills you would like to focus on in future training programs?\n",
    "Are you available to actively participate in testing communities and contribute to different activities that support their growth and development?\n",
    "Would you be open to sharing your expertise by leading training sessions within your field of knowledge?\n",
    "Would you be interested in joining Keystone MarketPlace Romania in the future?\nhttps://confluence.endava.com/spaces/CTO/pages/577044538/KMP+in+Romania",
    "Do you feel you have enough information or clarity regarding your next steps during bench period?\n",
    "Send Email",
]


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
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        print("Error: The selected Excel file is missing required columns:")
        for col in missing:
            print(f"  - {col}")
        input("Press Enter to return to the configuration menu...")
        from menu.options.configuration.configure import configure_options

        return configure_options()
    filtered = get_unsent_people(df)
    filtered = get_id_name_email(filtered)
    print("\nPeople who have NOT been sent an email:\n")
    display_people_table(filtered)
    input("\nPress Enter to return to the main menu...")
    main_menu()


if __name__ == "__main__":
    preview_file()
