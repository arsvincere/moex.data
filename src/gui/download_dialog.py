#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com


import enum
import logging
from datetime import date, time, timedelta, datetime
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from src.const import LIST_DIR
from src.moex import MoexData
from src.gui.custom import Palette, Font, Icon, ToolButton, HLine, Dialog
from src.gui.console import ConsoleWidget
from src.utils import Cmd
logger = logging.getLogger("LOGGER")

class TGetFirsDate(QtCore.QThread):
    def __init__(self, moex, tree, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.moex = moex
        self.tree = tree

    def run(self):
        logger.info(f":: Receiving first date")
        for i in self.tree:
            ticker = i.ticker
            dt = self.moex.getFirstDatetime(ticker)
            if dt is not None:
                dt = dt.strftime("%Y-%m-%d %H:%M")
                i.setText(Tree.Column.FIRST_DATE, dt)
                logger.info(f"  - received first date for {ticker} -> {dt}")
            else:
                i.setText(Tree.Column.FIRST_DATE, "None")
        logger.info(f"Receive complete!")


class TGetLastDate(QtCore.QThread):
    def __init__(self, moex, tree, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.moex = moex
        self.tree = tree

    def run(self):
        logger.info(f":: Checkin last date")
        for i in self.tree:
            ticker = i.ticker
            dt = self.moex.getLastDatetime(ticker)
            if dt is not None:
                dt = dt.strftime("%Y-%m-%d %H:%M")
                i.setText(Tree.Column.LAST_DATE, dt)
                i.setCheckState(Tree.Column.SECID, Qt.CheckState.Checked)
            else:
                i.setText(Tree.Column.LAST_DATE, "None")
        logger.info(f"Chekin complete!")


class TDownload(QtCore.QThread):
    def __init__(self, moex, shares, timeframe_list, begin, end, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.moex = moex
        self.shares = shares
        self.timeframe_list = timeframe_list
        self.begin = begin
        self.end = end

    def run(self):
        logger.info(f":: Start download data")
        for i in self.shares:
            for timeframe in self.timeframe_list:
                ticker = i.ticker
                if self.begin is None:
                    self.begin = self.moex.getFirstDatetime(ticker).year
                year = self.begin
                while year <= self.end:
                    self.moex.download(ticker, timeframe, year)
                    year += 1
        logger.info(f"Download complete!")


class TUpdate(QtCore.QThread):
    def __init__(self, moex, shares, timeframe_list, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.moex = moex
        self.shares = shares
        self.timeframe_list = timeframe_list

    def run(self):
        logger.info(f":: Start update data")
        for i in self.shares:
            for timeframe in self.timeframe_list:
                ticker = i.ticker
                self.moex.update(ticker, timeframe)
        logger.info(f"Update complete!")


class TDelete(QtCore.QThread):
    def __init__(self, moex, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.moex = moex

    def run(self):
        logger.info(f":: Delete moex data")
        self.moex.deleteMoexData()
        logger.info(f"Delete complete!")


class IShare(QtWidgets.QTreeWidgetItem):
    def __init__(self, dct, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setCheckState(0, Qt.CheckState.Unchecked)
        self.setText(Tree.Column.SECID,     str(dct["SECID"]))
        self.setText(Tree.Column.SECNAME,   str(dct["SECNAME"]))

    @property  #ticker
    def ticker(self):
        logger.debug(f"{self.__class__.__name__}.ticker")
        return self.text(Tree.Column.SECID)


class Tree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        SECID =                 enum.auto(0),
        SECNAME =               enum.auto(),
        FIRST_DATE =            enum.auto(),
        LAST_DATE =             enum.auto(),

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()

    def __iter__(self):
        logger.debug(f"{self.__class__.__name__}.__iter__()")
        all_items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            all_items.append(item)
        return iter(all_items)

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(Tree.Column.SECID, Qt.SortOrder.AscendingOrder)
        self.setFont(Font.MONO)
        self.setColumnWidth(Tree.Column.SECID, 100)
        self.setColumnWidth(Tree.Column.SECNAME, 250)
        self.setColumnWidth(Tree.Column.FIRST_DATE, 150)
        self.setColumnWidth(Tree.Column.LAST_DATE, 150)
        self.setMinimumWidth(700)

    def getSelected(self):
        logger.debug(f"{self.__class__.__name__}.getSelected()")
        selected = list()
        for i in self:
            if i.checkState(Tree.Column.SECID) == Qt.CheckState.Checked:
                selected.append(i)
        return selected

    def setSharesList(self, slist):
        logger.debug(f"{self.__class__.__name__}.setSharesList()")
        for i in slist:
            item = IShare(i)
            self.addTopLevelItem(item)


class DownloadDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__configSpinBox()
        self.__connect()
        self.__checkGeneralSharesList()
        self.__loadSharesList()
        self.__initUI()
        self.thread = None

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tree = Tree(self)
        self.btn_close = ToolButton(Icon.CLOSE)
        self.combobox_list = QtWidgets.QComboBox(self)
        self.btn_download = QtWidgets.QPushButton("Download")
        self.btn_update = QtWidgets.QPushButton("Update")
        self.btn_first = QtWidgets.QPushButton("Refresh", self)
        self.btn_last = QtWidgets.QPushButton("Refresh", self)
        self.first_availible = QtWidgets.QCheckBox("From first availible")
        self.begin_year = QtWidgets.QSpinBox(self)
        self.end_year = QtWidgets.QSpinBox(self)
        self.checkbox_1M = QtWidgets.QCheckBox("1M", self)
        self.checkbox_10M = QtWidgets.QCheckBox("10M", self)
        self.checkbox_1H = QtWidgets.QCheckBox("1H", self)
        self.checkbox_D = QtWidgets.QCheckBox("D", self)
        self.checkbox_W = QtWidgets.QCheckBox("W", self)
        self.checkbox_M = QtWidgets.QCheckBox("M", self)
        self.info_label = QtWidgets.QLabel(
            "\n"
            "If you have downloaded data\n"
            "and want to get new candles\n"
            "from a previous date, click\n"
            "the 'Update' button:"
            )
        self.log = ConsoleWidget(self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox_top_btn = QtWidgets.QHBoxLayout()
        hbox_top_btn.addStretch()
        hbox_top_btn.addWidget(self.btn_close)
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.checkbox_1M,    0, 0)
        grid.addWidget(self.checkbox_10M,   1, 0)
        grid.addWidget(self.checkbox_1H,    2, 0)
        grid.addWidget(self.checkbox_D,     0, 1)
        grid.addWidget(self.checkbox_W,     1, 1)
        grid.addWidget(self.checkbox_M,     2, 1)
        timeframes = QtWidgets.QGroupBox("Timeframe:")
        timeframes.setLayout(grid)
        form = QtWidgets.QFormLayout()
        form.addRow(                    hbox_top_btn)
        form.addRow(                    HLine(self))
        form.addRow(" ",                QtWidgets.QLabel(" "))
        form.addRow("Asset list",       self.combobox_list)
        form.addRow("First date",       self.btn_first)
        form.addRow("Last date",        self.btn_last)
        form.addRow(                    self.first_availible)
        form.addRow("Begin",            self.begin_year)
        form.addRow("End",              self.end_year)
        form.addRow(                    timeframes)
        form.addRow(                    self.btn_download)
        form.addRow(                    self.info_label)
        form.addRow(                    self.btn_update)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.tree)
        vbox.addWidget(self.log)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addLayout(form)
        self.setLayout(hbox)

    def __configSpinBox(self):
        logger.debug(f"{self.__class__.__name__}.__configSpinBox()")
        self.setWindowTitle("Download Tinkoff data")
        now_year = date.today().year
        first_year = 1997
        self.begin_year.setMinimum(first_year)
        self.begin_year.setMaximum(now_year)
        self.begin_year.setValue(first_year)
        self.end_year.setMinimum(first_year)
        self.end_year.setMaximum(now_year)
        self.end_year.setValue(now_year)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_close.clicked.connect(self.__onClose)
        self.combobox_list.currentTextChanged.connect(self.__updateTree)
        self.btn_first.clicked.connect(self.__onRefreshFirstDate)
        self.btn_last.clicked.connect(self.__onRefreshLastDate)
        self.first_availible.clicked.connect(self.__onCheckFirstAvailible)
        self.btn_download.clicked.connect(self.__onDownload)
        self.btn_update.clicked.connect(self.__onUpdate)

    def __checkGeneralSharesList(self):
        logger.debug(f"{self.__class__.__name__}.__checkGeneralSharesList()")
        if not Cmd.isExist(LIST_DIR):
            Cmd.createDirs(LIST_DIR)
        path = Cmd.join(LIST_DIR, "all.json")
        if not Cmd.isExist(path):
            md = MoexData()
            full_list = md.getAllShares()
            MoexData.saveSharesList(full_list, "all")

    def __loadSharesList(self):
        logger.debug(f"{self.__class__.__name__}.__loadAssetLists()")
        files = Cmd.getFiles(LIST_DIR, full_path=False)
        for file in files:
            name = Cmd.name(file)
            self.combobox_list.addItem(name)

    def __initUI(self):
        logger.debug(f"{self.__class__.__name__}.__initUI()")
        self.first_availible.setChecked(True)
        self.begin_year.setEnabled(False)
        self.checkbox_1M.setChecked(True)

    def __getSelectedShares(self):
        logger.debug(f"{self.__class__.__name__}.__getSelectedShares()")
        shares_items = self.tree.getSelected()
        if len(shares_items) == 0:
            logger.warning(f"No selected shares")
        return shares_items

    def __getSelectedTimeframes(self):
        logger.debug(f"{self.__class__.__name__}.__getSelectedTimeframes()")
        tf_list = list()
        if self.checkbox_1M.isChecked(): tf_list.append("1m")
        if self.checkbox_10M.isChecked(): tf_list.append("10m")
        if self.checkbox_1H.isChecked(): tf_list.append("1h")
        if self.checkbox_D.isChecked(): tf_list.append("D")
        if self.checkbox_W.isChecked(): tf_list.append("W")
        if self.checkbox_M.isChecked(): tf_list.append("M")
        if len(tf_list) == 0:
            logger.warning(f"No selected timeframes")
        return tf_list

    def __getBeginYear(self):
        logger.debug(f"{self.__class__.__name__}.__getBeginYear()")
        if self.first_availible.isChecked():
            return None
        else:
            return self.begin_year.value()

    def __getEndYear(self):
        logger.debug(f"{self.__class__.__name__}.__getEndYear()")
        return self.end_year.value()

    @QtCore.pyqtSlot()  #__threadFinished
    def __threadFinished(self):
        logger.debug(f"{self.__class__.__name__}.__threadFinished()")
        self.thread = None
        self.btn_download.setEnabled(True)
        self.btn_update.setEnabled(True)

    @QtCore.pyqtSlot()  #__updateTree
    def __updateTree(self):
        logger.debug(f"{self.__class__.__name__}.__updateTree()")
        self.tree.clear()
        list_name = self.combobox_list.currentText()
        shares_list = MoexData.loadSharesList(list_name)
        self.tree.setSharesList(shares_list)

    @QtCore.pyqtSlot()  #__onHelp
    def __onHelp(self):
        logger.debug(f"{self.__class__.__name__}.__onHelp()")
        ...

    @QtCore.pyqtSlot()  #__onClose
    def __onClose(self):
        logger.debug(f"{self.__class__.__name__}.__onClose()")
        QtWidgets.QApplication.instance().quit()

    @QtCore.pyqtSlot()  #__onCheckFirstAvailible
    def __onCheckFirstAvailible(self):
        logger.debug(f"{self.__class__.__name__}.__onCheckFirstAvailible()")
        if self.first_availible.isChecked():
            self.begin_year.setEnabled(False)
        else:
            self.begin_year.setEnabled(True)

    @QtCore.pyqtSlot()  #__onRefreshFirstDate
    def __onRefreshFirstDate(self):
        logger.debug(f"{self.__class__.__name__}.__onRefreshFirstDate()")
        if self.thread is not None:
            Dialog.info(f"Data manager is busy now, wait for complete task")
            return
        md = MoexData()
        self.thread = TGetFirsDate(md, self.tree)
        self.thread.finished.connect(self.__threadFinished)
        self.thread.start()

    @QtCore.pyqtSlot()  #__onRefreshLastDate
    def __onRefreshLastDate(self):
        logger.debug(f"{self.__class__.__name__}.__onRefreshLastDate()")
        if self.thread is not None:
            Dialog.info(f"Data manager is busy now, wait for complete task")
            return
        md = MoexData()
        self.thread = TGetLastDate(md, self.tree)
        self.thread.finished.connect(self.__threadFinished)
        self.thread.start()

    @QtCore.pyqtSlot()  #__onDownload
    def __onDownload(self):
        logger.debug(f"{self.__class__.__name__}.__onDownload()")
        shares = self.__getSelectedShares()
        if len(shares) == 0:
            Dialog.info("No selected shares\nChoose share before")
            return
        timeframe_list = self.__getSelectedTimeframes()
        if len(timeframe_list) == 0:
            Dialog.info("No selected timeframe\nChoose timeframe before")
            return
        begin = self.__getBeginYear()
        end = self.__getEndYear()
        md = MoexData()
        self.thread = TDownload(md, shares, timeframe_list, begin, end)
        self.thread.finished.connect(self.__threadFinished)
        self.thread.start()
        self.btn_download.setEnabled(False)
        self.btn_update.setEnabled(False)

    @QtCore.pyqtSlot()  #__onUpdate
    def __onUpdate(self):
        logger.debug(f"{self.__class__.__name__}.__onUpdate()")
        shares = self.__getSelectedShares()
        if len(shares) == 0:
            Dialog.info("No selected shares\nChoose share before")
            return
        timeframe_list = self.__getSelectedTimeframes()
        if len(timeframe_list) == 0:
            Dialog.info("No selected timeframe\nChoose timeframe before")
            return
        md = MoexData()
        self.thread = TUpdate(md, shares, timeframe_list)
        self.thread.finished.connect(self.__threadFinished)
        self.thread.start()
        self.btn_download.setEnabled(False)
        self.btn_update.setEnabled(False)



if __name__ == "__main__":
    ...

