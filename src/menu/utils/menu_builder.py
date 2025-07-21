import msvcrt
from menu.utils.logo import get_logo
import os


def menu_builder(title, menu_items, header=None):
    """
    Displays an interactive terminal menu based on a list of items with associated callbacks.

    Args:
        title (str): The title to display above the menu.
        menu_items (list of dict): Each item must have 'label' and 'callback' keys.
        header (str, optional): Text to display under the logo and above the title.
    """
    selected = 0
    while True:
        get_logo()
        if header:
            print(header)
        print(f"\n{title}")
        for idx, item in enumerate(menu_items):
            prefix = "-> " if idx == selected else "   "
            print(f"{prefix}{idx + 1}. {item['label']}")
        print("\nUse Up/Down arrows to move, Enter to select.")

        key = msvcrt.getch()
        if key == b"\xe0":
            key2 = msvcrt.getch()
            if key2 == b"H":
                selected = (selected - 1) % len(menu_items)
            elif key2 == b"P":
                selected = (selected + 1) % len(menu_items)
        elif key == b"\r":
            get_logo()
            if header:
                print(header)
            return menu_items[selected]["callback"]()
