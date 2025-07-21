import pandas as pd


def find_column(df, keyword: str) -> str:
    for col in df.columns:
        if keyword.lower() in col.lower():
            return col
    raise ValueError(f"Could not find column with keyword: '{keyword}'")


def get_entries_for_unsent(df: pd.DataFrame) -> list[dict]:
    col_interest = find_column(df, "upskilling")
    col_motivation = find_column(df, "future training programs")
    col_enrolled = find_column(df, "next period")
    col_email = find_column(df, "email")
    col_name = find_column(df, "name")
    col_status = find_column(df, "send email")
    col_coach = find_column(df, "career coach")

    entries = []

    for _, row in df[df[col_status] != 1].iterrows():
        entry = {
            "name": str(row[col_name]).strip(),
            "email": str(row[col_email]).strip(),
            "career_coach": str(row[col_coach]).strip(),
            "r1": str(row[col_interest]).strip() or "-",
            "r2": str(row[col_motivation]).strip() or "-",
            "r3": str(row[col_enrolled]).strip() or "-",
        }
        entries.append(entry)

    return entries
