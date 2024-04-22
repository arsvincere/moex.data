#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """

import logging
from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from moexalgo import Market, Ticker
from moexalgo.models import Candle
from src.const import LIST_DIR, DOWNLOAD_DIR, ONE_DAY
from src.utils import Cmd
logger = logging.getLogger("LOGGER")

@dataclass  #Bar
class Bar():
    dt:     datetime | str
    open:   float
    high:   float
    low:    float
    close:  float
    vol:    int

    def __post_init__(self):
        if isinstance(self.dt, str):
            self.dt = datetime.fromisoformat(self.dt)

    @staticmethod  #toCSV
    def toCSV(bar):
        dt = bar.dt.isoformat()
        s = f"'{dt}',{bar.open},{bar.high},{bar.low},{bar.close},{bar.vol}"
        return s

    @staticmethod  #fromCSV
    def fromCSV(bar_str):
        code = f"Bar({bar_str})"
        bar = eval(code)
        return bar


class MoexData():
    def __init__(self):
        logger.debug(f"{self.__class__.__name__}.__init__")
        ...

    def __toTimedelta(self, timeframe: str):
        logger.debug(f"{self.__class__.__name__}.__checkTimeFrame")
        if timeframe not in "1m 10m 1h D W M":
            logger.error(f"Uncorrect timeframe='{timeframe}'")
            return
        period = {
            "1m":   timedelta(minutes=1),
            "10m":  timedelta(minutes=10),
            "1h":   timedelta(hours=1),
            "D":    timedelta(days=1),
            "W":    timedelta(days=1),  # calm down, it works
            "M":    timedelta(days=1),  # calm down, it works
            }
        return period[timeframe]

    def __createDirPath(self, ticker, timeframe):
        dir_path = Cmd.join(
            DOWNLOAD_DIR,
            ticker,
            timeframe,
            )
        Cmd.createDirs(dir_path)
        return dir_path

    def __createFilePath(self, ticker, timeframe, year):
        dir_path = self.__createDirPath(ticker, timeframe)
        file_name = f"{ticker}-{timeframe}-{year}.csv"
        full_path = Cmd.join(dir_path, file_name)
        return full_path

    def __format(self, candle: Candle):
        line = (
            f"{candle.begin.isoformat()};"
            f"{candle.end.isoformat()};"
            f"{candle.open};"
            f"{candle.high};"
            f"{candle.low};"
            f"{candle.close};"
            f"{candle.value};"
            f"{int(candle.volume)};"
            )
        return line

    def __header(self):
        """ Возвращает строку заголовок для .csv файлов с данными
        --
        При работе с .csv некоторым бывает удобно сразу в файл записать
        зоголовки для столбцов. Эта функция создает строку, которую
        будет использовать функция MoexData.__save() при сохранении файла.
        По умолчанию сохраняются все поля полученные от Мос.биржи
        --
        Отредактируйте строку 'header' в удобный для вас формат
        при этом не забудьте изменить функцию MoexData.__format()
        чтобы порядок записи данных соответствовал заголовку.
        """
        header = "<begin>;<end>;<open>;<high>;<low>;<close>;<value>;<volume>"
        return header

    def __toCSV(self, candles):
        text = list()
        for i in candles:
            line = self.__format(i) + "\n"
            text.append(line)
        return text

    def __save(self, candles, path):
        text = list()
        header = self.__header()
        text.append(header + "\n")
        text += self.__toCSV(candles)
        Cmd.save(text, path)

    def __findLastFile(self, ticker, timeframe):
        dir_path = Cmd.join(
            DOWNLOAD_DIR,
            ticker,
            timeframe,
            )
        if not Cmd.isExist(dir_path):
            return None
        files = sorted(Cmd.getFiles(dir_path, full_path=True))
        if len(files) == 0:
            return None
        last_file = files[-1]
        return last_file

    def __popYear(self, candles, year):
        extract = list()
        while len(candles) > 0 and candles[0].begin.year == year:
            candle = candles.pop(0)
            extract.append(candle)
        return extract

    def __addNewCandles(self, ticker, timeframe, new_candles):
        year = self.getLastDatetime(ticker, timeframe).year
        current_year_part = self.__popYear(new_candles, year)
        new_csv_rows = self.__toCSV(current_year_part)
        last_file_path = self.__findLastFile(ticker, timeframe)
        Cmd.append(new_csv_rows, last_file_path)
        # Смотрим остались ли еще новые свечи (если на новый год попали)
        while len(new_candles) > 0:
            current_year_part = self.__popYear(new_candles, year)
            path = self.__createFilePath(ticker, timeframe, year)
            self.__save(current_year_part, path)
            year += 1

    @staticmethod  #saveSharesList
    def saveSharesList(shares, name):
        path = Cmd.join(LIST_DIR, f"{name}.json")
        Cmd.saveJSON(shares, path)

    @staticmethod  #loadSharesList
    def loadSharesList(name):
        path = Cmd.join(LIST_DIR, f"{name}.json")
        obj = Cmd.loadJSON(path)
        return obj

    def getAllShares(self) -> list:
        shares = Market("stocks").tickers()
        return shares

    def getFirstDatetime(self, ticker: str, timeframe="1m"):
        """ Receive first 1M candle from MOEX, and return his datetime """
        date_start = datetime(1900, 1, 1)
        try:
            share = Ticker(ticker)
            candles = share.candles(
                date=       date_start,
                till_date=  "today",
                period=     timeframe,
                limit=      1,  #  candles count
                )
        except KeyError as err:
            logger.warning(f"MoexData: no market data for {ticker}")
            return None
        candle = candles.send(None)
        dt = candle.begin
        return dt

    def getLastDatetime(self, ticker: str, timeframe="1m"):
        """ Return last downloaded datetime for ticker/timeframe
        --
        Search in downloaded data file '{ticker}-{timeframe}-{last_year}.csv
        return datetime of latest candle.
        --
        If file not exist return None
        """
        last_file = self.__findLastFile(ticker, timeframe)
        if last_file is None:
            return None
        text = Cmd.load(last_file)
        last_row = text[-1]
        dt = last_row.split(";")[0]
        dt = datetime.fromisoformat(dt)
        return dt

    def getCandles(self, ticker, timeframe, begin, end):
        all_candles = list()
        dt = begin
        while dt < end:
            logger.info(f"  - request {ticker}-{timeframe} {dt.date()}")
            # download in parts by day
            share = Ticker(ticker)
            candles = share.candles(
                date=       dt,
                till_date=  datetime.combine(dt.date(), time(23,59)),
                period=     timeframe,
            )
            for i in candles:
                all_candles.append(i)
            dt += ONE_DAY
        return all_candles

    def download(self, ticker, timeframe, year):
        logger.info(f":: Download {ticker}-{timeframe} from {year}")
        begin = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
        if end >= datetime.now():
            end = datetime.combine(date.today(), time(0, 0))
        candles = self.getCandles(ticker, timeframe, begin, end)
        if len(candles) == 0:
            logger.warning(f"No data for {ticker}-{timeframe}-{year}!")
            return
        path = self.__createFilePath(ticker, timeframe, year)
        self.__save(candles, path)
        logger.info(f"Saved {ticker}-{timeframe}-{year} in {path}")

    def update(self, ticker, timeframe):
        last_dt = self.getLastDatetime(ticker, timeframe)
        if last_dt is None:
            logger.warning(
                f"{ticker}-{timeframe} not exist data. "
                f"Need download data before update. "
                f"Update {ticker} canceled"
                )
            return
        logger.info(f":: Update data for {ticker}-{timeframe}")
        new_candles = self.getCandles(
            ticker=     ticker,
            timeframe=  timeframe,
            begin=      last_dt + self.__toTimedelta(timeframe),
            end=        datetime.combine(date.today(), time(0, 0))
            )
        count = len(new_candles)
        logger.info(f"{ticker}-{timeframe} received {count} canlde")
        self.__addNewCandles(ticker, timeframe, new_candles)
        logger.info(f"{ticker}-{timeframe} new candles saved")

    def deleteMoexData(self):
        path = Cmd.join(DOWNLOAD_DIR, MoexData.DIR_NAME)
        dirs = Cmd.getDirs(path, full_path=True)
        for i in dirs:
            logger.info(f"  - delete moex data '{i}'")
            Cmd.deleteDir(i)




if __name__ == "__main__":
    ...

