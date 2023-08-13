from __future__ import annotations

import os

# Directories
MODULE_FOLDER = os.path.dirname(os.path.abspath(__file__))
APP_FOLDER = os.path.dirname(os.path.dirname(MODULE_FOLDER))

# Files
CONFIG_FILE = os.path.join(APP_FOLDER, "config.yml")
