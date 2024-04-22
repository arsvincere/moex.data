#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import logging
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from src.utils import Cmd
from src.const import RES_DIR
logger = logging.getLogger("LOGGER")

class GuiError(Exception): pass

class Color():
    DARK =              QtGui.QColor("#0F0F0F")  #5
    NORMAL =            QtGui.QColor("#323232")
    INACTIVE =          QtGui.QColor("#373737")  #4
    HIGHLIGHT =         QtGui.QColor("#5D5E60")  #3
    DISABLED_TEXT =     QtGui.QColor("#848388")  #2
    TEXT =              QtGui.QColor("#B7B7AF")  #1
    BUTTON_TEXT =       QtGui.QColor("#CCCCCC")
    WINDOW_TEXT =       QtGui.QColor("#EEEEEE")
    HIGHLIGHT_TEXT =    QtGui.QColor("#FAFAFA")

class Font():
    MONO = QtGui.QFont("monospace")
    SANS = QtGui.QFont("sans")

class Icon():
    CLOSE =     QtGui.QIcon(Cmd.join(RES_DIR, "close.svg"))

class Palette(QtGui.QPalette):
    def __init__(self):
        QtGui.QPalette.__init__(self)
        g = QtGui.QPalette.ColorGroup
        r = QtGui.QPalette.ColorRole
        c = Color
        self.setColor(g.Normal,    r.Window,           c.NORMAL)
        self.setColor(g.Inactive,  r.Window,           c.INACTIVE)
        self.setColor(g.Disabled,  r.Window,           c.INACTIVE)
        self.setColor(g.Normal,    r.Base,             c.NORMAL)
        self.setColor(g.Inactive,  r.Base,             c.INACTIVE)
        self.setColor(g.Disabled,  r.Base,             c.INACTIVE)
        self.setColor(g.Normal,    r.Button,           c.NORMAL)
        self.setColor(g.Inactive,  r.Button,           c.INACTIVE)
        self.setColor(g.Disabled,  r.Button,           c.NORMAL)
        self.setColor(g.Normal,    r.Highlight,        c.HIGHLIGHT)
        self.setColor(g.Inactive,  r.Highlight,        c.HIGHLIGHT)
        self.setColor(g.Normal,    r.HighlightedText,  c.HIGHLIGHT_TEXT)
        self.setColor(g.Inactive,  r.HighlightedText,  c.HIGHLIGHT_TEXT)
        self.setColor(g.Normal,    r.WindowText,       c.WINDOW_TEXT)
        self.setColor(g.Inactive,  r.WindowText,       c.WINDOW_TEXT)
        self.setColor(g.Disabled,  r.WindowText,       c.DISABLED_TEXT)
        self.setColor(g.Normal,    r.ButtonText,       c.BUTTON_TEXT)
        self.setColor(g.Inactive,  r.ButtonText,       c.BUTTON_TEXT)
        self.setColor(g.Disabled,  r.ButtonText,       c.DISABLED_TEXT)
        self.setColor(g.Normal,    r.Text,             c.TEXT)
        self.setColor(g.Inactive,  r.Text,             c.TEXT)
        self.setColor(g.Disabled,  r.Text,             c.DISABLED_TEXT)


class Spacer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
            )


class HLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)


class VLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)


class ProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent=None):
        QtWidgets.QProgressBar.__init__(self, parent)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setMaximumHeight(20)
        self.setFont(Font.MONO)


class ToolButton(QtWidgets.QToolButton):
    """ Const """
    HEIGHT = 32
    WIDTH =  32
    SIZE =   QtCore.QSize(WIDTH, HEIGHT)

    def __init__(self, icon, parent=None):
        QtWidgets.QToolButton.__init__(self, parent)
        self.setIcon(icon)
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setIconSize(self.SIZE)


class SmallButton(QtWidgets.QToolButton):
    """ Const """
    HEIGHT = 16
    WIDTH =  16
    SIZE =   QtCore.QSize(WIDTH, HEIGHT)

    def __init__(self, icon, parent=None):
        QtWidgets.QToolButton.__init__(self, parent)
        self.setIcon(icon)
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setIconSize(self.SIZE)
        self.setContentsMargins(0, 0, 0, 0)


class Dialog(QtWidgets.QDialog):
    class _DialogInfo(QtWidgets.QDialog):
        def __init__(self, parent=None):
            QtWidgets.QDialog.__init__(self, parent)
            self.__config()
            self.__createWidgets()
            self.__createLayots()
            self.__connect()

        def __config(self):
            self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        def __createWidgets(self):
            self.__message_label = QtWidgets.QLabel()
            self.__btn_ok = ToolButton(Icon.OK)

        def __createLayots(self):
            hbox = QtWidgets.QHBoxLayout()
            hbox.addWidget(self.__message_label)
            hbox.addWidget(self.__btn_ok)
            self.setLayout(hbox)

        def __connect(self):
            self.__btn_ok.clicked.connect(self.accept)

        def info(self, message):
            self.__message_label.setText(message)
            self.exec()


    class _DialogConfirm(QtWidgets.QDialog):
        def __init__(self, parent=None):
            QtWidgets.QDialog.__init__(self, parent)
            self.__createWidgets()
            self.__createLayots()
            self.__configButton()
            self.__config()
            self.__connect()

        def __createWidgets(self):
            self.__message_label = QtWidgets.QLabel()
            self.__btn_yes = QtWidgets.QToolButton(self)
            self.__btn_no = QtWidgets.QToolButton(self)

        def __createLayots(self):
            btn_box = QtWidgets.QHBoxLayout()
            btn_box.addStretch()
            btn_box.addWidget(self.__btn_yes)
            btn_box.addWidget(self.__btn_no)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(self.__message_label)
            vbox.addLayout(btn_box)
            self.setLayout(vbox)

        def __configButton(self):
            self.__btn_yes.setFixedSize(32, 32)
            self.__btn_yes.setIcon(Icon.YES)
            self.__btn_yes.setIconSize(QtCore.QSize(32, 32))
            self.__btn_no.setFixedSize(32, 32)
            self.__btn_no.setIcon(Icon.NO)
            self.__btn_no.setIconSize(QtCore.QSize(32, 32))

        def __config(self):
            self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        def __connect(self):
            self.__btn_yes.clicked.connect(self.accept)
            self.__btn_no.clicked.connect(self.reject)

        def confirm(self, message):
            self.__message_label.setText(message)
            result = self.exec()
            if result == QtWidgets.QDialog.DialogCode.Accepted:
                return True
            else:
                return False


    class _DialogName(QtWidgets.QDialog):
        def __init__(self, parent=None):
            QtWidgets.QDialog.__init__(self, parent)
            self.__createWidgets()
            self.__createLayots()
            self.__configButton()
            self.__config()
            self.__connect()

        def __createWidgets(self):
            self.__lineedit = QtWidgets.QLineEdit("Enter name")
            self.__btn_yes = QtWidgets.QToolButton(self)
            self.__btn_no = QtWidgets.QToolButton(self)

        def __createLayots(self):
            btn_box = QtWidgets.QHBoxLayout()
            btn_box.addStretch()
            btn_box.addWidget(self.__btn_yes)
            btn_box.addWidget(self.__btn_no)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(self.__lineedit)
            vbox.addLayout(btn_box)
            self.setLayout(vbox)

        def __configButton(self):
            self.__btn_yes.setFixedSize(32, 32)
            self.__btn_yes.setIcon(Icon.YES)
            self.__btn_yes.setIconSize(QtCore.QSize(32, 32))
            self.__btn_no.setFixedSize(32, 32)
            self.__btn_no.setIcon(Icon.NO)
            self.__btn_no.setIconSize(QtCore.QSize(32, 32))

        def __config(self):
            self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        def __connect(self):
            self.__btn_yes.clicked.connect(self.accept)
            self.__btn_no.clicked.connect(self.reject)

        def enterName(self, message):
            self.__lineedit.setText(message)
            result = self.exec()
            if result == QtWidgets.QDialog.DialogCode.Accepted:
                name = self.__lineedit.text()
                return name
            else:
                return False


    class _DialogOffer(QtWidgets.QDialog):
        def __init__(self, parent=None):
            QtWidgets.QDialog.__init__(self, parent)
            self.__createWidgets()
            self.__createLayots()
            self.__configButton()
            self.__config()
            self.__connect()

        def __createWidgets(self):
            self.__lineedit = QtWidgets.QLineEdit("Enter name")
            self.__btn_yes = QtWidgets.QToolButton(self)
            self.__btn_no = QtWidgets.QToolButton(self)

        def __createLayots(self):
            btn_box = QtWidgets.QHBoxLayout()
            btn_box.addStretch()
            btn_box.addWidget(self.__btn_yes)
            btn_box.addWidget(self.__btn_no)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(self.__lineedit)
            vbox.addLayout(btn_box)
            self.setLayout(vbox)

        def __configButton(self):
            self.__btn_yes.setFixedSize(32, 32)
            self.__btn_yes.setIcon(Icon.YES)
            self.__btn_yes.setIconSize(QtCore.QSize(32, 32))
            self.__btn_no.setFixedSize(32, 32)
            self.__btn_no.setIcon(Icon.NO)
            self.__btn_no.setIconSize(QtCore.QSize(32, 32))

        def __config(self):
            self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        def __connect(self):
            self.__btn_yes.clicked.connect(self.accept)
            self.__btn_no.clicked.connect(self.reject)

        def enterName(self, message):
            self.__lineedit.setText(message)
            result = self.exec()
            if result == QtWidgets.QDialog.DialogCode.Accepted:
                name = self.__lineedit.text()
                return name
            else:
                return False


    @staticmethod  #info
    def info(message):
        dial = Dialog._DialogInfo()
        dial.info(message)

    @staticmethod  #confirm
    def confirm(message="Ты хорошо подумал?"):
        dial = Dialog._DialogConfirm()
        result = dial.confirm(message)
        return result

    @staticmethod  #name
    def name(default="Enter name"):
        dial = Dialog._DialogName()
        name = dial.enterName(default)
        return name



if __name__ == "__main__":
    ...

