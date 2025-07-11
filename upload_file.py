import requests
from auth import get_token

def upload_file(local_path, remote_name):
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }

    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_name}:/content"

    with open(local_path, "rb") as f:
        response = requests.put(url, headers=headers, data=f)

    if response.status_code in (200, 201):
        print(f"Fișierul '{remote_name}' a fost încărcat cu succes.")
    else:
        print("Eroare la upload:", response.status_code, response.text)

if __name__ == "__main__":
    upload_file("fisier_test.txt", "FolderTest/fisier_test.txt")
