from tkinter import filedialog, Tk
from menu.utils.config_manager import load_config, save_config
import pandas as pd

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


def set_survey_path():
    root = Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select Survey Excel File", filetypes=[("Excel files", "*.xlsx")]
    )
    root.destroy()

    if path:
        try:
            df = pd.read_excel(path)
            missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            if missing:
                print("Error: The selected Excel file is missing required columns:")
                for col in missing:
                    print(f"  - {col}")
                input("Press Enter to return to the configuration menu...")
                from menu.options.configuration.configure import configure_options

                return configure_options()
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            input("Press Enter to return to the configuration menu...")
            from menu.options.configuration.configure import configure_options

            return configure_options()
        config = load_config()
        config["Paths"]["survey_path"] = path
        save_config(config)
        print(f"Survey path saved to config.ini.")
    else:
        print("No file selected.")
    input("Press Enter to return to the configuration menu...")
    from menu.options.configuration.configure import configure_options

    configure_options()
