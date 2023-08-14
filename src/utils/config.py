from __future__ import annotations

import yaml

from src.utils import constants


conf: dict = {}


def config() -> dict:
    """
    Loads the config.yaml file and returns a dict
    stored in config
    Returns:
        dict: configuration dictionary
    """

    global conf
    if not conf:
        with open(constants.CONFIG_FILE, encoding="utf-8") as cfg:
            conf = yaml.load(cfg, Loader=yaml.loader.SafeLoader)
    return conf
