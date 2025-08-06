import os
import pandas as pd
import win32com.client as win32

from menu.options.send_emails.llm_integration.run import generate_llm_outputs
from menu.utils.config_manager import get_survey_path, get_llm_path
from menu.options.send_emails.llm_integration.survey_parser import find_column
from menu.options.send_emails.llm_integration.sent_log import (
    load_sent_log,
    append_to_sent_log,
)

# === CONFIG ===
subject = "Your Development Plan – Personalized Suggestions"
LOG_PATH = "C:\\Users\\iustanciu\\OneDrive - ENDAVA\\Survey\\sent_log.xlsx"

EMAIL_TEMPLATE = """
<html>
<body>
<p>Hello <b>{name}</b>,</p>
<p>Thank you for completing the form! I’d like to share some valuable information to support your
upskilling and certification journey.</p>
{generated_section}
<p>These resources will help you develop your skills in the fields you’re most
passionate about. Feel free to explore the available materials, and don’t hesitate to reach out to Local
Community Leads if you have any questions or need further support.</p>
<p style="margin-top: 20px;"><b>Romania Testing Technical Communities: Collaboration & Knowledge Hub</b></p>
</body>
</html>
"""


def send_email_outlook(to: str, cc: str, subject: str, html_body: str):
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = to
    mail.CC = cc
    mail.Subject = subject
    mail.HTMLBody = html_body
    mail.Send()


def send_all_emails():
    survey_path = get_survey_path()
    llm_model_path = get_llm_path()

    if not survey_path or not os.path.exists(survey_path):
        print("Survey file not found. Please configure the path in the options menu.")
        input("Press Enter to return to the menu...")
        return

    if not llm_model_path or not os.path.exists(llm_model_path):
        print("LLM model not found. Please configure the path in the options menu.")
        input("Press Enter to return to the menu...")
        return

    if os.path.getsize(llm_model_path) < 4 * 1024 * 1024 * 1024:
        print("LLM model file is smaller than 4GB. Please select a valid model.")
        input("Press Enter to return to the menu...")
        return

    try:
        df = pd.read_excel(survey_path)

        required_keywords = [
            "upskilling",
            "future training programs",
            "next period",
            "email",
            "name",
            "career coach",
            "id",
        ]
        for keyword in required_keywords:
            find_column(df, keyword)

        sent_ids = load_sent_log(LOG_PATH)
        responses = generate_llm_outputs(df)

        if not responses:
            print("All entries are already processed. No emails were sent.")
            input("Press Enter to return to the menu...")
            return

        for entry in responses:
            entry_id = str(entry["id"]).strip()
            if entry_id in sent_ids:
                print(f"Skipping Id {entry_id} (already sent)")
                continue

            try:
                html = EMAIL_TEMPLATE.format(
                    name=entry["name"], generated_section=entry["llm_output"]
                )
                print(
                    f"Sending to {entry['name']} <{entry['email']}> | CC: {entry['coach']}"
                )
                send_email_outlook(
                    to=entry["email"],
                    cc=entry["coach"],
                    subject=subject,
                    html_body=html,
                )
                append_to_sent_log(entry_id, "Success", path=LOG_PATH)

            except Exception as e:
                print(f"Failed to send email to Id {entry_id}: {e}")
                append_to_sent_log(entry_id, f"Failed: {str(e)}", path=LOG_PATH)

        print("All emails processed and log updated.")

    except ValueError as e:
        print(f"\nMissing required column in survey file: {e}")
        input("Press Enter to return to the menu...")
    except PermissionError:
        print("\nPermission denied. The survey file is likely open elsewhere.")
        print("Please close the file and try again.")
        input("Press Enter to return to the menu...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        input("Press Enter to return to the menu...")


if __name__ == "__main__":
    send_all_emails()
