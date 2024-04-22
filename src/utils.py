#!/usr/bin/env python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

import os
import sys
import json
import enum
import pickle
import shutil
import bisect
import zipfile
import logging
import subprocess
from pprint import pprint
from collections import deque
from datetime import datetime, date, time, timedelta
sys.path.append("/home/alex/yandex/avin-dev/avin/")
from src.const import UTC

logger = logging.getLogger("LOGGER")


def now():
    return datetime.utcnow().replace(tzinfo=UTC)

def encodeJSON(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, avin.core.TimeFrame):
        return str(obj)
    if isinstance(obj, enum.Enum):
        return str(obj)
    if isinstance(obj, (avin.core.Asset)):
        return avin.core.Asset.toJSON(obj)

def decodeJSON(obj):
    for k, v in obj.items():
        if isinstance(v, str) and "+00:00" in v:
            obj[k] = datetime.fromisoformat(obj[k])
        if k == "timeframe_list":
            tmp = list()
            for string in obj["timeframe_list"]:
                timeframe = avin.core.TimeFrame(string)
                tmp.append(timeframe)
            obj["timeframe_list"] = tmp
        if k == "timeframe":
            obj["timeframe"] = avin.core.TimeFrame(obj["timeframe"])
        if k == "asset":
            obj["asset"] = avin.core.Asset.fromJSON(obj["asset"])
        if isinstance(v, str) and "Type.SHORT" in v:
            obj[k] = avin.core.Signal.Type.SHORT
        if isinstance(v, str) and "Type.LONG" in v:
            obj[k] = avin.core.Signal.Type.LONG
    return obj


class Cmd():
    @staticmethod  #join
    def join(*path):
        logger.debug(f"Cmd.join({path})")
        path = os.path.join(*path)
        return path

    @staticmethod  #name
    def name(file_path, extension=False):
        """ -- Doc
        Отделяет имя файла из пути к файлу
        /home/file_name.txt -> file_name.txt  # extension=True
        /home/file_name.txt -> file_name  # extension=False
        """
        logger.debug(f"Cmd.name({file_path}, extension={extension}")
        file_name = os.path.basename(file_path)  # == somename.xxx
        if extension:
            return file_name
        else:
            name = os.path.splitext(file_name)[0]  # == somename
            return name

    @staticmethod  #dirName
    def dirName(file_path):
        logger.debug(f"Cmd.dirName({file_path}")
        dir_path = os.path.dirname(file_path)
        dir_name = os.path.basename(dir_path)
        return dir_name

    @staticmethod  #dirPath
    def dirPath(file_path):
        logger.debug(f"Cmd.dirPath({file_path}")
        dir_path = os.path.dirname(file_path)
        return dir_path

    @staticmethod  #isExist
    def isExist(path):
        logger.debug(f"Cmd.isExist({path})")
        return os.path.exists(path)

    @staticmethod  #isFile
    def isFile(path):
        logger.debug(f"Cmd.isFile({path})")
        return os.path.isfile(path)

    @staticmethod  #isDir
    def isDir(path):
        logger.debug(f"Cmd.isFile({path})")
        return os.path.isdir(path)

    @staticmethod  #contents
    def contents(dir_path, full_path=False):
        logger.debug(f"Cmd.getFiles({dir_path}, full_path={full_path})")
        list_dirs_files = list()
        names = os.listdir(dir_path)
        for name in names:
            if full_path:
                path = Cmd.join(dir_path, name)
                list_dirs_files.append(path)
            else:
                list_dirs_files.append(name)
        return list_dirs_files

    @staticmethod  #getFiles
    def getFiles(dir_path, full_path=False):
        logger.debug(f"Cmd.getFiles({dir_path}, full_path={full_path})")
        list_files = list()
        names = os.listdir(dir_path)
        for name in names:
            path = Cmd.join(dir_path, name)
            if os.path.isfile(path):
                if full_path:
                    list_files.append(path)
                else:
                    list_files.append(name)
        return list_files

    @staticmethod  #getDirs
    def getDirs(dir_path, full_path=False):
        """ -- Doc
        Возвращает список папок в каталоге 'dir_path' без обхода подпапок
        """
        logger.debug(f"Cmd.getDirs({dir_path}, full_path={full_path})")
        list_dirs = list()
        names = os.listdir(dir_path)
        for name in names:
            path = Cmd.join(dir_path, name)
            if os.path.isdir(path):
                if full_path:
                    list_dirs.append(path)
                else:
                    list_dirs.append(name)
        return list_dirs

    @staticmethod  #createDirs
    def createDirs(path):
        """ Создает все необходимые папки для этого пути """
        try:
            os.makedirs(path)
            logger.debug(f"Create dirs: {path}")
        except FileExistsError as err:
            pass  # Если папка уже существует просто выходим

    @staticmethod  #deleteDir
    def deleteDir(path):
        shutil.rmtree(path)
        logger.debug(f"Delete dir: {path}")

    @staticmethod  #extractArchive
    def extractArchive(archive_path, dest_dir):
        with zipfile.ZipFile(archive_path, "r") as file:
            file.extractall(dest_dir)
        logger.debug(f"Extracted archive: '{archive_path}'")

    @staticmethod  #findFile
    def findFile(file_name, dir_path):
        logger.debug(f"Cmd.findFile({file_name}, {dir_path})")
        for root, dirs, files in os.walk(dir_path):
            if file_name in files:
                return os.path.join(root, file_name)
            else:
                raise FileNotFoundError(f"Файл '{file_name}' не найден "
                                         "в директории '{dir_path}'")

    @staticmethod  #findDir
    def findDir(dir_name, root_dir):
        logger.debug(f"Cmd.findDir({dir_name}, {root_dir})")
        for root, dirs, files in os.walk(root_dir):
            if dir_name in dirs:
                return os.path.join(root, dir_name)
        raise FileNotFoundError(f"Папка '{dir_name}' не найдена "
                                 "в директории '{root_dir}'")

    @staticmethod  #select
    def select(files, extension):
        """ Возвращает список файлов c расширением 'extension' """
        selected = list()
        for file in files:
            if file.endswith(extension):
                selected.append(file)
        return selected

    @staticmethod  #rename
    def rename(old_path, new_path):
        """ Переименовывает old_path в new_path"""
        os.rename(old_path, new_path)

    @staticmethod  #replace
    def replace(src, dest):
        """ Перемещает src в dest """
        os.replace(src, dest)

    @staticmethod  #copyFile
    def copyFile(src, dest):
        """ Копирует src в dest """
        shutil.copy(src, dest)

    @staticmethod  #copyDir
    def copyDir(src, dest):
        """ Копирует src в dest """
        shutil.copytree(src, dest)

    @staticmethod  #delete
    def delete(file_path):
        """ Удаляет файла по указанному пути """
        os.remove(file_path)
        logger.debug(f"Delete: {file_path}")

    @staticmethod  #subprocess
    def subprocess(command):
        logger.debug(f"Cmd.subprocess({command}")
        """
        import platform
        import subprocess
        # define a command that starts new terminal
        if platform.system() == "Windows":
            new_window_command = "cmd.exe /c start".split()
        else:
            new_window_command = "x-terminal-emulator -e".split()
        subprocess.check_call(new_window_command + command)
        """
        # command = [program, file_path]
        # new_window_command = "x-terminal-emulator -e".split()
        # new_window_command = "xterm -e".split()
        # new_window_command = ("xfce4-terminal", "-x")
        subprocess.call(command)

    @staticmethod  #save
    def save(text: list[str], file_path: str) -> bool:
        with open(file_path, "w", encoding="utf-8") as file:
            for line in text:
                file.write(line)
        logger.debug(f"Save file: {file_path}")
        return True

    @staticmethod  #load
    def load(file_path: str) -> list[str]:
        """ Read file by row, return <class list[<class str>]> """
        text = list()
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                text.append(line)
        logger.debug(f"Cmd.load: {file_path}")
        return text

    @staticmethod  #read
    def read(file_path: str) -> str:
        """ Read file as one string, return <class str> """
        text = ""
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        logger.debug(f"Cmd.read: {file_path}")
        return text

    @staticmethod  #append
    def append(text, file_path):
        with open(file_path, "a", encoding="utf-8") as file:
            for line in text:
                file.write(line)
        logger.debug(f"Cmd.append(text): {file_path}")
        return True

    @staticmethod  #getTail
    def getTail(file_path, n):
        """ идиотский способ на самом деле.
        по сути он же читает весь файл построчно и добавляет его в
        очередь, у которой максимальная длина n... таким образом
        дойдя до конца файла в очереди останется n последних строк
        - тогда уж проще прочитать весь файл и взять N последний строк
        """
        with open(file_path, "r", encoding="utf-8") as file:
            text = list(deque(file, n))
        return text

    @staticmethod  #saveJSON
    def saveJSON(obj, file_path, encoder=encodeJSON, indent=4):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                obj=obj,
                fp=file,
                indent=indent,
                default=encoder,
                ensure_ascii=False,
                )
        logger.debug(f"Save json: {file_path}")

    @staticmethod  #loadJSON
    def loadJSON(file_path, decoder=decodeJSON):
        with open(file_path, "r", encoding="utf-8") as file:
            obj = json.load(
                fp=file,
                object_hook=decoder,
                )
        logger.debug(f"Load json: {file_path}")
        return obj

    @staticmethod  #saveBin
    def saveBin(self, file_path, silent=False, compress=False):
        if file_path == "auto":
            file_name = self.__autoFileName()
            dir_path = self.__autoDirPath()
            file_path = os.path.join(dir_path, file_name)
        fh = None
        try:
            if compress:
                fh = gzip.open(file_path, "wb")
            else:
                fh = open(file_path, "wb")
            pickle.dump([self.ID, self.timeframe, self.bars],
                        fh, pickle.HIGHEST_PROTOCOL)
            if not silent:
                print("SAVED:", file_path)
            return True
        except (EnvironmentError, pickle.PicklingError) as err:
            print("{0}: Ошибка сохранения: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()

    @staticmethod  #loadBin
    def loadBin(file_path, silent=False):
        GZIP_MAGIC = b"\x1F\x8B"  # метка .gzip файлов
        fh = None
        try:
            fh = open(file_path, "rb")
            magic = fh.read(len(GZIP_MAGIC))
            if magic == GZIP_MAGIC:
                fh.close()
                fh = gzip.open(file_path, "rb")
            else:
                fh.seek(0)
            ID, timeframe, bars = pickle.load(fh)
            if not silent:
                print("LOADED:", file_path)
            return Data.Data(ID, timeframe, bars)
        except (EnvironmentError, pickle.UnpicklingError) as err:
            print("{0}: Ошибка загрузки: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()



# ------- Remove it
# class UEncoder(json.JSONEncoder):
#         #Override the default method
#         def default(self, obj):
#             if isinstance(obj, (datetime, date)):
#                 return obj.isoformat()
#
# def UDecoder(dict_obj):
#     # One practice
#     for k, v in dict_obj.items():
#         if isinstance(v, str) and "+00:00" in v:
#             try:
#                 dict_obj[k] = datetime.datetime.fromisoformat(v)
#             except:
#                 pass
#     # Two practice
#     if "dt" in dict_obj:
#         dict_obj["dt"] = datetime.datetime.fromisoformat(dict_obj["dt"])
#     return dict_obj


if __name__ == "__main__":
    ...

