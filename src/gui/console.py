#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import logging
from datetime import datetime, date, time
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from src.gui.custom import Palette, Font
logger = logging.getLogger("LOGGER")

class Handler(logging.StreamHandler, QtCore.QObject):
    message = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        logging.StreamHandler.__init__(self)
        QtCore.QObject.__init__(self, parent)

    def emit(self, record):
        msg = self.format(record)
        self.message.emit(msg)
        self.flush()


class ConsoleWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        QtWidgets.QTabWidget.__init__(self, parent)
        self.__config()
        self.__createHandler()
        self.__createWidgets()
        self.__connect()
        logger.info("Welcome to MOEX Data Downloader!")
        logger.info("This program is a part of trade system 'Ars Vincere'")
        logger.info("For more details visit http://alexavin.blog ")

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setContentsMargins(0, 0, 0, 0)
        self.setFont(Font.MONO)
        self.setMaximumHeight(140)

    def __createHandler(self):
        logger.debug(f"{self.__class__.__name__}.__createTester()")
        self.handler = Handler(self)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
            )
        self.handler.setFormatter(formatter)
        self.handler.setLevel(logging.INFO)
        logger.addHandler(self.handler)

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.console = QtWidgets.QPlainTextEdit()
        self.addTab(self.console, "Log")

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.handler.message.connect(self.__updateText)

    def __scrollDown(self):
        scroll_bar = self.console.verticalScrollBar()
        end_text = scroll_bar.maximum()
        scroll_bar.setValue(end_text)

    def __updateText(self, msg):
        self.console.appendPlainText(msg)
        self.__scrollDown()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = ConsoleWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())

