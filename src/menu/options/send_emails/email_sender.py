import pandas as pd
import win32com.client as win32
from openpyxl import load_workbook
from llm_integration.run import generate_llm_outputs

# === CONFIG ===
xlsx_path = r"C:\Users\iustanciu\OneDrive - ENDAVA\Survey\BenchHub_Engagement & Upskilling Survey.xlsx"
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
    # citește Excel-ul complet (folosit doar pentru actualizare la final)
    df = pd.read_excel(xlsx_path)
    wb = load_workbook(xlsx_path)
    ws = wb.active

    col_send = [c for c in df.columns if "send email" in c.lower()][0]
    col_email = [c for c in df.columns if "email" in c.lower()][0]

    # generează textele și datele
    responses = generate_llm_outputs(xlsx_path)

    for idx, entry in enumerate(responses):
        name = entry["name"]
        email = entry["email"]
        coach = entry["coach"]
        body = entry["llm_output"]

        html = EMAIL_TEMPLATE.format(name=name, generated_section=body)

        print(f"Sending to {name} <{email}> | CC: {coach}")
        send_email_outlook(to=email, cc=coach, subject=subject, html_body=html)

        # caută rândul în Excel pentru actualizare
        excel_row = df[df[col_email] == email].index[0]
        ws.cell(row=excel_row + 2, column=df.columns.get_loc(col_send) + 1).value = 1

    wb.save(xlsx_path)
    print("All emails sent and Excel updated.")

if __name__ == "__main__":
    send_all_emails()
