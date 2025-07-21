import os

import pandas as pd
from tabulate import tabulate


def get_excel_df(EXCEL_PATH):
    try:
        df = pd.read_excel(EXCEL_PATH)
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        input("Press Enter to return to the preview menu...")
        return None


def truncate(val, width=40):
    val = str(val)
    return val if len(val) <= width else val[: width - 3] + "..."


def show_where_left_off(EXCEL_PATH):
    df = get_excel_df(EXCEL_PATH)
    if df is None:
        return
    unsent = df[df["Send Email"].astype(str).str.lower() == "no"]
    if not unsent.empty:
        print("You left off at:\n")
        row = unsent.head(1).transpose()
        row.columns = ["Next Person"]
        row = row.applymap(lambda x: truncate(x, 40))
        print(tabulate(row, headers="keys", tablefmt="grid", showindex=True))
    else:
        print("All emails have been sent!")
    input("\nPress Enter to return to the preview menu...")


def show_missed(EXCEL_PATH):
    df = get_excel_df(EXCEL_PATH)
    if df is None:
        return
    unsent = df[df["Send Email"].astype(str).str.lower() == "no"]
    if not unsent.empty:
        print(f"Missed {len(unsent)} recipients:\n")
        df_clean = unsent.transpose()
        df_clean.columns = [f"Person {i+1}" for i in range(len(df_clean.columns))]
        df_clean = df_clean.applymap(lambda x: truncate(x, 40))
        print(tabulate(df_clean, headers="keys", tablefmt="grid", showindex=True))
    else:
        print("No missed recipients!")
    input("\nPress Enter to return to the preview menu...")


def load_survey_df(EXCEL_PATH):
    """Load the survey Excel file as a DataFrame."""
    return get_excel_df(EXCEL_PATH)


def get_unsent_people(df):
    """Return a DataFrame of people who have not been sent an email (Send Email != 1)."""
    return df[df["Send Email"] != 1]


def get_id_name_email(df):
    """Return only the Id, Email, and Name columns from the DataFrame, if present."""
    cols = [col for col in df.columns if col.lower() in ["id", "name", "email"]]
    return df[cols]


def display_people_table(df):
    """Display the table of people in a readable format."""
    if df.empty:
        print("All emails have been sent!")
    else:
        print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))
