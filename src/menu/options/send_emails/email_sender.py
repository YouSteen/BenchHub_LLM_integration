import os
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

    try:
        df = pd.read_excel(survey_path)
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
    except PermissionError:
        print("\nPermission denied. Please close the Excel file before proceeding.")
        input("Press Enter to return to the menu...")
        return
    except ValueError as e:
        print(f"\nMissing required column: {e}")
        input("Press Enter to return to the menu...")
        return

    wb = load_workbook(survey_path)
    ws = wb.active

    if ws is None:
        raise ValueError("No active worksheet found in the Excel file.")

    col_send = find_column(df, "send email")
    col_email = find_column(df, "email")

    responses = generate_llm_outputs(df)

    for idx, entry in enumerate(responses):
        name = entry["name"]
        email = entry["email"]
        coach = entry["coach"]
        body = entry["llm_output"]

        html = EMAIL_TEMPLATE.format(name=name, generated_section=body)

        print(f"Sending to {name} <{email}> | CC: {coach}")
        send_email_outlook(to=email, cc=coach, subject=subject, html_body=html)

        matching_rows = df[df[col_email] == email]
        if not matching_rows.empty:
            excel_row = matching_rows.index[0]
            column_location = df.columns.get_loc(col_send)
            if isinstance(excel_row, int) and isinstance(column_location, int):
                ws.cell(row=excel_row + 2, column=column_location + 1).value = 1

    try:
        wb.save(survey_path)
    except PermissionError:
        print(
            "\nPermission denied. Could not save the Excel file. Please close it and try again."
        )
        input("Press Enter to return to the menu...")
        return

    print("All emails sent and Excel updated.")


if __name__ == "__main__":
    send_all_emails()
