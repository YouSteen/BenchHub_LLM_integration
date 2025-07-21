from tkinter import filedialog, Tk
from menu.utils.config_manager import load_config, save_config
import os


def set_llm_model_path():
    root = Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select LLM Model File", filetypes=[("GGUF files", "*.gguf")]
    )
    root.destroy()

    if path:
        if os.path.getsize(path) <= 4 * 1024 * 1024 * 1024:
            print(
                "Error: LLM model file must be over 4 GiB. Please select a valid model file."
            )
            input("Press Enter to return to the configuration menu...")
            from menu.options.configuration.configure import configure_options

            return configure_options()
        config = load_config()
        config["Paths"]["llm_model_path"] = path
        save_config(config)
        print(f"LLM model path saved to config.ini.")
    else:
        print("No file selected.")
    input("Press Enter to return to the configuration menu...")
    from menu.options.configuration.configure import configure_options

    configure_options()
