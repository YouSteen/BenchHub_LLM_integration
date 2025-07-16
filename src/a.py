import msal
import sys
import requests
import webbrowser

# ————————————————
# CONFIGURAȚIE APLICAȚIE MSAL
# ————————————————
CLIENT_ID = "2925c5fe-f4fd-4edb-99d1-4d2f703f0d1b"
AUTHORITY = "https://login.microsoftonline.com/0b3fc178-b730-4e8b-9843-e81259237b77"
SCOPES = [
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/Files.Read",
    "https://graph.microsoft.com/Sites.Read.All",
]

# ————————————————
# LOCAȚIE WHITELIST PE CLOUD
# ————————————————
DRIVE_ID = "b!S3Prhw2hHEWn7UN03_Oi2pBIKGHXwCNBuVM5m2H-ypjYLZcF2dGNQKT5LKlLzomK"
FILE_ID = "01S7UWZMWGQC7CVHLXMBAY7JS3KJKSQHW7"
# Linkul „People in ENDAVA” (copy link fără a da click pe Send):
WHITELIST_BROWSER_LINK = (
    "https://endava-my.sharepoint.com/:t:/g/personal/"
    "andrei_vataselu_endava_com/EcaAviqdd2BBj6ZbUlUoHt8B-wv4_u2zPdAJ3eKmuHgSyg"
    "?e=bMKaSo"
)

# ————————————————
# INITIALIZE MSAL
# ————————————————
app = msal.PublicClientApplication(client_id=CLIENT_ID, authority=AUTHORITY)


def validate_onedrive_access(token: str) -> bool:
    """Verifică dacă tokenul poate accesa OneDrive-ul utilizatorului."""
    resp = requests.get(
        "https://graph.microsoft.com/v1.0/me/drive/root",
        headers={"Authorization": f"Bearer {token}"},
    )
    print(f"[DEBUG] Verificare OneDrive: {resp.status_code}")
    return resp.status_code == 200


def fetch_whitelist(token: str) -> list[str]:
    """
    Încarcă whitelist-ul direct din fișierul share-uit pe SharePoint.
    Dacă dă 403, deschide link-ul în browser pentru ca tu să apeși „Open” o dată.
    """
    url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FILE_ID}/content"
    print(f"[DEBUG] Acces whitelist din cloud: {url}")
    resp = requests.get(
        url, headers={"Authorization": f"Bearer {token}", "Accept": "text/plain"}
    )

    if resp.status_code == 200:
        users = [l.strip().lower().replace(".", "") for l in resp.text.splitlines()]
        print(f"[DEBUG] Whitelist cloud: {users}")
        return users

    if resp.status_code == 403:
        print("[SECURITY] ❌ Acces blocat (403) la whitelist.")
        print("📎 Deschide fișierul în browser o dată:")
        print(f"🔗 {WHITELIST_BROWSER_LINK}")
        webbrowser.open(WHITELIST_BROWSER_LINK)
        return []

    print(f"[SECURITY] ⚠️ Eroare la fetch whitelist: {resp.status_code}")
    return []


def is_allowed(user_part: str, token: str) -> bool:
    """Verifică dacă user_part există în whitelist."""
    wl = fetch_whitelist(token)
    normalized = user_part.lower().replace(".", "")
    print(f"[DEBUG] Validare user: {normalized}")
    return normalized in wl


def main():
    print("[INFO] Autentificare securizată în curs...")

    # 1) Login interactiv MSAL
    try:
        result = app.acquire_token_interactive(scopes=SCOPES)
        print("[DEBUG] MSAL login OK.")
    except Exception as e:
        print(f"[ERROR] MSAL login failed: {e}")
        sys.exit(1)

    token = result.get("access_token")
    email = result.get("id_token_claims", {}).get("preferred_username")
    if not token or not email:
        print("[SECURITY] ❌ Token sau email lipsă.")
        sys.exit(1)

    print(f"[INFO] Logat ca: {email}")
    if not email.lower().endswith("@endava.com"):
        print("[SECURITY] ❌ Email non-Endava.")
        sys.exit(1)

    # 2) Verificare acces OneDrive
    if not validate_onedrive_access(token):
        print("[SECURITY] ❌ OneDrive inaccesibil.")
        sys.exit(1)

    # 3) Verificare whitelist
    user_part = email.split("@")[0]
    if not is_allowed(user_part, token):
        print("[SECURITY] ❌ Userul nu este în whitelist.")
        sys.exit(1)

    # 4) To do on success
    print(f"\n✅ [ACCESS GRANTED] Bine ai venit, {email}")
    # … restul aplicației …


if __name__ == "__main__":
    main()
