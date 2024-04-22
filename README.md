# moex.data - загрузка рыночных данных MOEX

![image](https://github.com/arsvincere/moex.data/blob/master/res/Screenshot_2024-04-22_13-42-22.png)

GUI утилита для загрузки исторических рыночных данных Московской биржи. Доступны таймфреймы: 1М, 10М, 1H, D, М, М.

## Зависимости

[PyQt6](https://pypi.org/project/PyQt6/) - набор расширений графического фреймворка Qt для языка программирования Python:

    pip install pyqt6
	
[moexalgo](https://github.com/moexalgo/moexalgo) - оффициальная библиотека Московской биржи для получения данных:

    pip install moexalgo

## Быстрый старт
**Запуск**
Выполнить файл main.py в корневой директории.
    
    python3 main.py

**Загрузка**
Отметить галочками нужные тикеры и таймфремы, нажать "Download"

**Обновление**
При нажатии кнопки "Update" для всех ранее скачанных данных будет выполнена загрузка только новых свечей.

## Настройка

### Список акций 
При первом запуске будет скачан список всех акций MOEX ./list/all.json
Вы можете скопировать этот файл, и удалить не нужные акции. Пользовательские списки будут доступны в комбобоксе 

### Пути к файлам
По умолчанию данные скачиваются в папку 'download' в корневой директории программы, в подпапки с названием тикера и таймфрейма.
Для изменения отредактируйте функцию moex.MoexData.__createDirPath

```python
    def __createDirPath(self, ticker, timeframe):
        dir_path = Cmd.join(
            DOWNLOAD_DIR,
            ticker,
            timeframe,
            )
        ...
```

### Имя файла с данными
Для изменения отредактируйте функцию moex.MoexData.__createFilePath

```python
    def __createFilePath(self, ticker, timeframe, year):
        ...
        file_name = f"{ticker}-{timeframe}-{year}.csv"
        ...
```

### Формат данных в .csv файле
Для изменения отредактируйте функцию moex.MoexData.__format

```python
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
        ...
```

### Header в .csv
Для изменения отредактируйте функцию moex.MoexData.__header

```python
    def __header(self):
        header = "<begin>;<end>;<open>;<high>;<low>;<close>;<value>;<volume>"
        ...
```

