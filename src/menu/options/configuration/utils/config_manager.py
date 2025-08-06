import os

APP_NAME = "BenchHubLLM"
CONFIG_FILENAME = "config.ini"


def get_config_path():
    """Get the full path to the config.ini inside AppData/Local."""
    appdata_dir = os.getenv("LOCALAPPDATA") or os.path.expanduser("~/.local/share")
    config_dir = os.path.join(appdata_dir, APP_NAME)
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, CONFIG_FILENAME)


def save_config(config):
    """Save the current config to the file."""
    with open(get_config_path(), "w") as f:
        config.write(f)
