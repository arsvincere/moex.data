#!/usr/bin/env  python3
# FILE:         main.py
# CREATED:      2024.04.04
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc
Программа загружает рыночные данные по акциям Московской биржи

Использует официальную библиотеку 'moexalgo'.
Доступные таймфреймы: '1m', '10m', '1h', 'D', 'W', 'M'

"""

import sys
import logging
import PyQt6
from src.gui.download_dialog import DownloadDialog
from src.gui.custom import Palette
from src.const import LOG_DIR, LOG_FILE
from src.utils import Cmd


def main():
    configLogger("LOGGER")
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = DownloadDialog()
    w.show()
    code = app.exec()
    sys.exit(code)

def configLogger(name: str) -> None:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not Cmd.isExist(LOG_DIR):
        Cmd.createDirs(LOG_DIR)
    # create file handler
    file_formatter = logging.Formatter(
        "%(module)s: %(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        )
    file_handler = logging.FileHandler(LOG_FILE, mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

if __name__ == "__main__":
    main()

