import requests
import pandas as pd
from io import BytesIO
from auth import get_token
from tabulate import tabulate

def read_benchhub_survey():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    
    folder = "Survey"
    file_name = "BenchHubEngagement & Upskilling Survey.xlsx"

   
    encoded_file = file_name.replace(" ", "%20").replace("&", "%26")
    download_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder}/{encoded_file}:/content"

    response = requests.get(download_url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Eroare la descărcarea fișierului {file_name}:", response.text)

    df = pd.read_excel(BytesIO(response.content))

    print(f"Fișierul '{file_name}' a fost citit cu succes.")
    print("Primele răspunsuri din survey:")
    print(df.head())

    return df


def select_upskilling_columns(df):
    df.columns = df.columns.str.strip()  

    selected_cols = [
        "E-mail",
        "Which areas of upskilling are you most interested in? (You can select multiple options)",
        "Are there any specific topics or skills you would like to focus on in future training programs?",
        "Any certificate that you have in mind for the next period?"
    ]

    df_filtered = df[selected_cols]

    print("\n Upskilling responses (coloane relevante):")
    print(tabulate(df_filtered, headers="keys", tablefmt="grid", showindex=False))

    return df_filtered


if __name__ == "__main__":
    df = read_benchhub_survey()
    select_upskilling_columns(df)

    # print("Coloane disponibile:")
    # for col in df.columns:
    #     print(f"- '{col}'")

