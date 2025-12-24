import json
import logging
import os
import time
import requests
from urllib3 import Retry
from itertools import chain
from .misc import ThreadPool
from .dictionary.base import SimpleWord
from requests.adapters import HTTPAdapter
from .queryApi.base import AbstractQueryAPI, QueryAPIReturnType
from aqt.qt import QObject, pyqtSignal, QThread
from .exceptions import BalanceInsufficientException
from typing import Type, Optional, Any, Protocol
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class CheckCookieProtocol(Protocol):
    def __call__(self, cookie: dict[str, Any]) -> bool: ...


class LoginStateCheckWorker(QObject):
    start = pyqtSignal()
    logSuccess = pyqtSignal(str)
    logFailed = pyqtSignal()

    def __init__(self, checkFn: CheckCookieProtocol, cookie: dict[str, Any]):
        super().__init__()
        self.checkFn = checkFn
        self.cookie = cookie

    def run(self):
        loginState = self.checkFn(self.cookie)
        if loginState:
            self.logSuccess.emit(json.dumps(self.cookie))
        else:
            self.logFailed.emit()


class RemoteWordFetchingWorker(QObject):
    start = pyqtSignal()
    tick = pyqtSignal()
    setProgress = pyqtSignal(int)
    done = pyqtSignal()
    doneThisGroup = pyqtSignal(list)
    logger = logging.getLogger("Apora dict2Anki.workers.RemoteWordFetchingWorker")

    def __init__(self, selectedDict, selectedGroups: list[tuple]):
        super().__init__()
        self.selectedDict = selectedDict
        self.selectedGroups = selectedGroups

    def run(self):
        currentThread = QThread.currentThread()

        def _pull(*args):
            if currentThread.isInterruptionRequested():  # type: ignore
                return
            wordPerPage = self.selectedDict.getWordsByPage(*args)
            self.tick.emit()
            return wordPerPage

        for groupName, groupId in self.selectedGroups:
            totalPage = self.selectedDict.getTotalPage(groupName, groupId)
            self.setProgress.emit(totalPage)
            with ThreadPool(max_workers=3) as executor:
                for i in range(totalPage):
                    executor.submit(_pull, i, groupName, groupId)
            remoteWordList = list(chain(*[ft for ft in executor.result]))
            self.doneThisGroup.emit(remoteWordList)

        self.done.emit()


class QueryWorker(QObject):
    start = pyqtSignal()
    tick = pyqtSignal()
    thisRowDone = pyqtSignal(int, QueryAPIReturnType)
    thisRowFailed = pyqtSignal(int)
    allQueryDone = pyqtSignal()
    insufficientBalance = pyqtSignal()
    logger = logging.getLogger("Apora dict2Anki.workers.QueryWorker")

    def __init__(
        self,
        wordList: list[tuple[SimpleWord, int]],
        api: Type[AbstractQueryAPI],
        max_workers: int = 3,  # concurrent number
        delay: float = 0,  # delay seconds for api query
    ):
        super().__init__()
        self.wordList = wordList
        self.api = api
        self.max_workers = max_workers
        self.delay = delay
        self._stop_flag = threading.Event()

    def run(self):
        currentThread = QThread.currentThread()

        def _query(word: SimpleWord, row) -> Optional[QueryAPIReturnType]:
            if currentThread.isInterruptionRequested():  # type: ignore
                return
            queryResult: QueryAPIReturnType | None = None
            try:
                queryResult = self.api.query(word)
            except BalanceInsufficientException:
                self.logger.error(f"余额不足，停止所有查询: {word}")
                self._stop_flag.set()  # 设置停止标志
                self.insufficientBalance.emit()  # 通知 UI
            except Exception as e:
                self.logger.exception(f"查询时发生未预期错误 ({word}): {e}")
                self.thisRowFailed.emit(row)
                self.tick.emit()
                return None

            if queryResult:
                self.logger.info(f"查询成功: {word} -- {queryResult}")
                self.thisRowDone.emit(row, queryResult)
            else:
                self.logger.warning(f"查询失败: {word}")
                self.thisRowFailed.emit(row)

            self.tick.emit()
            return queryResult

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for word, row in self.wordList:
                if self._stop_flag.is_set():
                    break

                if self.delay > 0 and len(futures) > 0:
                    time.sleep(self.delay)

                # check interruption
                if currentThread and currentThread.isInterruptionRequested():
                    break
                future = executor.submit(_query, word, row)
                futures.append(future)

            for future in as_completed(futures):
                # 可以在这里处理 future.result()，但通常不需要
                pass

        self.allQueryDone.emit()


class AssetDownloadWorker(QObject):
    """Asset (Image and Audio) download worker"""

    start = pyqtSignal()
    tick = pyqtSignal()
    done = pyqtSignal()
    logger = logging.getLogger("Apora dict2Anki.workers.AudioDownloadWorker")
    retries = Retry(total=5, backoff_factor=3, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    def __init__(
        self,
        target_dir,
        images: list[tuple[str, str]],  # list[tuple[filename, file download url]]
        audios: list[tuple[str, str]],  # list[tuple[filename, file download url]]
        overwrite=False,
        max_retry=3,
    ):
        super().__init__()
        self.target_dir = target_dir
        self.images = images
        self.audios = audios
        self.overwrite = overwrite
        self.max_retry = max_retry

    def run(self):
        currentThread = QThread.currentThread()

        def __download_with_retry(filename, url):
            success = False
            for i in range(self.max_retry):
                if __download(filename, url):
                    success = True
                    break
                if currentThread.isInterruptionRequested():  # type: ignore
                    success = False
                    break
                self.logger.info(f"Retrying {i + 1} time...")
            if success:
                self.tick.emit()
            else:
                self.logger.error(
                    f"FAILED to download {fileName} after retrying {self.max_retry} times!"
                )
                self.logger.info("----------------------------------")

        def __download(fileName, url) -> bool:
            """Do NOT call this method directly. Use `__download_with_retry` instead."""
            filepath = os.path.join(self.target_dir, fileName)
            try:
                if currentThread.isInterruptionRequested():  # type: ignore
                    return False
                self.logger.info(f"Downloading {fileName}...")
                # file already exists
                if os.path.exists(filepath):
                    if not self.overwrite:
                        self.logger.info(f"[SKIP] {fileName} already exists")
                        return True
                    else:
                        self.logger.warning(f"Overwriting file {fileName}")

                r = self.session.get(url, stream=True)
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                self.logger.info(f"[OK] {fileName} 下载完成")
                self.logger.info("----------------------------------")
                return True
            except Exception as e:
                self.logger.warning(f"下载{fileName}:{url}异常: {e}")
                return False

        with ThreadPool(max_workers=3) as executor:
            # download images
            for fileName, url in self.images:
                executor.submit(__download_with_retry(fileName, url))
            # download audios
            for fileName, url in self.audios:
                executor.submit(__download_with_retry, fileName, url)
        self.done.emit()

    @classmethod
    def close(cls):
        cls.session.close()
