from menu.options.configuration.paths.llm_path import set_llm_model_path
from menu.options.configuration.paths.survey_path import set_survey_path
from menu.utils.menu_builder import menu_builder
from menu.utils.config_manager import load_config


def configure_options():
    from menu.handler import main_menu  # defer import to avoid circular ref

    # Load current config
    config = load_config()
    llm_model = config["Paths"].get("llm_model_path", "<not set>")
    survey = config["Paths"].get("survey_path", "<not set>")

    header = (
        f"\nCurrent Configuration:\n"
        f"  🔹 LLM Model Path:   {llm_model}\n"
        f"  🔹 Survey Path:      {survey}\n"
    )

    menu_items = [
        {"label": "Configure LLM Model Path", "callback": set_llm_model_path},
        {"label": "Configure Survey Path", "callback": set_survey_path},
        {"label": "Go back to main menu", "callback": main_menu},
    ]
    menu_builder("Configuration Options:", menu_items, header=header)
