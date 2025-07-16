import msal
import os
import json
from config import client_id, authority, scopes

CACHE_FILE = "token_cache.json"


def load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        cache.deserialize(open(CACHE_FILE, "r").read())
    return cache


def save_cache(cache):
    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())


def start_device_flow():
    cache = load_cache()
    app = msal.PublicClientApplication(
        client_id=client_id, authority=authority, token_cache=cache
    )
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        raise Exception(f"Autentificarea nu a putut fi inițiată: {flow}")
    return flow, app, cache


def complete_device_flow(flow, app, cache):
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" in result:
        save_cache(cache)
        return result["access_token"]
    else:
        raise Exception("Autentificare eșuată:", result.get("error_description"))


def get_token():
    cache = load_cache()
    app = msal.PublicClientApplication(
        client_id=client_id, authority=authority, token_cache=cache
    )
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            save_cache(cache)
            return result["access_token"]
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        raise Exception(f"Autentificarea nu a putut fi inițiată: {flow}")
    print("Mergi la:", flow["verification_uri"])
    print("Introdu codul:", flow["user_code"])
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" in result:
        print("Token obținut cu succes.")
        save_cache(cache)
        return result["access_token"]
    else:
        raise Exception("Autentificare eșuată:", result.get("error_description"))
