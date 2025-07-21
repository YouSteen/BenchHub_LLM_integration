from menu.utils.menu_builder import menu_builder
from menu.options.send_emails.email_sender import send_all_emails
from menu.options.configuration.configure import configure_options
from menu.options.preview.preview import preview_file
from menu.options.exit.exit import exit_app


def main_menu():
    while True:
        menu_items = [
            {"label": "Run Email Sender", "callback": send_all_emails},
            {"label": "Configure Options", "callback": configure_options},
            {"label": "Preview File", "callback": preview_file},
            {"label": "Exit", "callback": exit_app},
        ]
        menu_builder("BenchHub LLM Integration Menu:", menu_items)


if __name__ == "__main__":
    main_menu()
