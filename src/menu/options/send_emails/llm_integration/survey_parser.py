import pandas as pd

def find_column(df, keyword: str) -> str:
    for col in df.columns:
        if keyword.lower() in col.lower():
            return col
    raise ValueError(f"Could not find column with keyword: '{keyword}'")

def load_all_form_responses(xlsx_path: str) -> list[tuple[str, str, str]]:
    df = pd.read_excel(xlsx_path)

    col_interest = find_column(df, "upskilling")
    col_motivation = find_column(df, "future training programs")
    col_enrolled = find_column(df, "next period")

    responses = []
    for _, row in df.iterrows():
        r1 = str(row.get(col_interest, "")).strip() or "-"
        r2 = str(row.get(col_motivation, "")).strip() or "-"
        r3 = str(row.get(col_enrolled, "")).strip() or "-"
        responses.append((r1, r2, r3))

    return responses


# if __name__ == "__main__":
#     responses = load_all_form_responses(r"C:\Users\iustanciu\OneDrive - ENDAVA\Survey\BenchHub_Engagement & Upskilling Survey.xlsx")
#     for r in responses:
#         print(r)
