import os
import pandas as pd
from datetime import datetime

LOG_PATH = "C:\\Users\\iustanciu\\OneDrive - ENDAVA\\Survey\\sent_log.xlsx"

def load_sent_log(path: str = LOG_PATH) -> set:
    if not os.path.exists(path):
        df = pd.DataFrame(columns=["Id", "Timestamp", "Status"])
        df.to_excel(path, index=False)
        return set()
    df = pd.read_excel(path)
    return set(df["Id"].dropna().astype(str).str.strip())

def append_to_sent_log(entry_id: str, status: str, path: str = LOG_PATH):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {"Id": entry_id, "Timestamp": timestamp, "Status": status}

    if not os.path.exists(path):
        df = pd.DataFrame(columns=["Id", "Timestamp", "Status"])
    else:
        df = pd.read_excel(path)

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(path, index=False)
