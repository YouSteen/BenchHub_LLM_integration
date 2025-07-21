import os
import shutil
import pandas as pd
import win32com.client as win32
from openpyxl import load_workbook

from menu.options.send_emails.llm_integration.run import generate_llm_outputs
from menu.utils.config_manager import get_survey_path, get_llm_path
from menu.options.send_emails.llm_integration.survey_parser import find_column

# === CONFIG ===
subject = "Your Development Plan – Personalized Suggestions"

EMAIL_TEMPLATE = """
<html>
<body>
<p>Hello <b>{name}</b>,</p>
<p>Thank you for completing the form! I’d like to share some valuable information to support your upskilling and certification journey.</p>
{generated_section}
<p>These resources will help you develop your skills in the fields you’re most passionate about. Feel free to explore the available materials, and don’t hesitate to reach out to Local Community Leads if you have any questions or need further support.</p>
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

    temp_survey_path = "temp_survey.xlsx"
    try:
        shutil.copy(survey_path, temp_survey_path)
    except (FileNotFoundError, PermissionError):
        print(
            "\nPermission denied or file not found. Please check the survey path and ensure the file is not open elsewhere."
        )
        input("Press Enter to return to the menu...")
        return
    except Exception as e:
        print(f"\nError copying survey file: {e}")
        input("Press Enter to return to the menu...")
        return

    try:
        df = pd.read_excel(temp_survey_path)
        wb = load_workbook(temp_survey_path)
        ws = wb.active

        required_keywords = [
            "upskilling",
            "future training programs",
            "next period",
            "email",
            "name",
            "send email",
            "career coach",
        ]
        for keyword in required_keywords:
            find_column(df, keyword)

        if ws is None:
            raise ValueError("No active worksheet found in the Excel file.")

        col_send = find_column(df, "send email")
        col_email = find_column(df, "email")
        responses = generate_llm_outputs(df)

        for entry in responses:
            html = EMAIL_TEMPLATE.format(
                name=entry["name"], generated_section=entry["llm_output"]
            )
            print(
                f"Sending to {entry['name']} <{entry['email']}> | CC: {entry['coach']}"
            )
            send_email_outlook(
                to=entry["email"], cc=entry["coach"], subject=subject, html_body=html
            )

            matching_rows = df[df[col_email] == entry["email"]]
            if not matching_rows.empty:
                excel_row = matching_rows.index[0]
                column_location = df.columns.get_loc(col_send)
                if isinstance(excel_row, int) and isinstance(column_location, int):
                    ws.cell(row=excel_row + 2, column=column_location + 1).value = 1

        wb.save(temp_survey_path)
        shutil.move(temp_survey_path, survey_path)
        print("All emails sent and Excel updated.")

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
    finally:
        if os.path.exists(temp_survey_path):
            os.remove(temp_survey_path)


if __name__ == "__main__":
    send_all_emails()
