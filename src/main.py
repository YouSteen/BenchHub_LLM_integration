import sys
import os
from menu.handler import main_menu

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


if __name__ == "__main__":
    main_menu()
