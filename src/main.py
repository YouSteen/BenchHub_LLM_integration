import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from menu.handler import main_menu

if __name__ == "__main__":
    main_menu()
