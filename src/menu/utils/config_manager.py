import os
import configparser

APP_NAME = "BenchHubLLM"
CONFIG_FILENAME = "config.ini"


def get_config_path():
    """Get the full path to the config.ini inside AppData/Local."""
    appdata_dir = os.getenv("LOCALAPPDATA") or os.path.expanduser("~/.local/share")
    config_dir = os.path.join(appdata_dir, APP_NAME)
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, CONFIG_FILENAME)


def load_config():
    """Load config.ini or create it with defaults if not exists."""
    config_path = get_config_path()
    config = configparser.ConfigParser()

    if not os.path.exists(config_path):
        config["Paths"] = {"llm_model_path": "", "survey_path": ""}
        with open(config_path, "w") as f:
            config.write(f)
    else:
        config.read(config_path)

    return config


def save_config(config):
    """Save the current config to the file."""
    with open(get_config_path(), "w") as f:
        config.write(f)
