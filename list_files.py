import requests
from auth import get_token

def list_onedrive_files():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
    response = requests.get(url, headers=headers)
    data = response.json()

    print("Fișiere din OneDrive:")
    for item in data.get("value", []):
        print(item["name"])

if __name__ == "__main__":
    list_onedrive_files()
