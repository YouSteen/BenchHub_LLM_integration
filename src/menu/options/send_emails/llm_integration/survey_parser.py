import pandas as pd


def find_column(df, keyword: str) -> str:
    for col in df.columns:
        if keyword.lower() in col.lower():
            return col
    raise ValueError(f"Could not find column with keyword: '{keyword}'")


def get_entries_for_unsent(df: pd.DataFrame, sent_ids: set) -> list[dict]:
    col_interest = find_column(df, "upskilling")
    col_motivation = find_column(df, "future training programs")
    col_enrolled = find_column(df, "next period")
    col_email = find_column(df, "email")
    col_name = find_column(df, "name")
    col_coach = find_column(df, "career coach")
    col_id = find_column(df, "Id")

    entries = []

    for _, row in df.iterrows():
        entry_id = str(row[col_id]).strip()
        if entry_id in sent_ids:
            continue  # skip if already sent

        entry = {
            "id": entry_id,
            "name": str(row[col_name]).strip(),
            "email": str(row[col_email]).strip(),
            "career_coach": str(row[col_coach]).strip(),
            "r1": str(row[col_interest]).strip() or "-",
            "r2": str(row[col_motivation]).strip() or "-",
            "r3": str(row[col_enrolled]).strip() or "-",
        }
        entries.append(entry)

    return entries

