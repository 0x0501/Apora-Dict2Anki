import time
import logging
import requests
import requests.utils
from math import ceil
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from ..misc import safe_load_config_from_mw, Language, ConfigType
from dataclasses import dataclass
from ..constants import HEADERS
from .base import AbstractDictionary, SimpleWord
from ..misc import CredentialPlatformEnum

logger = logging.getLogger("Apora dict2Anki.dictionary.eudict")


@dataclass
class Validation:
    name: str
    baseUrl: str
    checkUrl: str


class Eudict(AbstractDictionary):
    platform = CredentialPlatformEnum.EUDIC
    name = "欧陆词典"
    timeout = 10
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    config: ConfigType
    validations = {
        "en": Validation(
            name="English", baseUrl="my.eudic.net", checkUrl="dict.eudic.net"
        ),
        "fr": Validation(
            name="French", baseUrl="my.frdic.com", checkUrl="www.frdic.com"
        ),
    }

    def __init__(self):
        self.groups = []
        self.indexSoup = None
        self.config = safe_load_config_from_mw()

    @staticmethod
    def getLoginUrl() -> str:
        config = safe_load_config_from_mw()

        if config.language == Language.ENGLISH:
            return "https://dict.eudic.net/account/login"  # for English
        else:
            return "https://www.frdic.com/account/login"  # for French

    def checkCookie(self, cookie: dict) -> bool:
        """
        cookie有效性检验
        :param cookie:
        :return: Boolean cookie是否有效
        """

        # Empty dict return False
        if len(cookie) == 0:
            return False

        validation = self.validations[self.config.language.value]

        rsp = requests.get(
            f"https://{validation.baseUrl}/studylist",
            cookies=cookie,
            headers=HEADERS,
            allow_redirects=True,
        )

        if f"{validation.checkUrl}/account/login" not in rsp.url:
            self.indexSoup = BeautifulSoup(rsp.text, features="html.parser")
            logger.info("Cookie有效")
            cookiesJar = requests.utils.cookiejar_from_dict(
                cookie, cookiejar=None, overwrite=True
            )
            self.session.cookies = cookiesJar
            return True
        logger.info("Cookie失效")
        return False

    @staticmethod
    def loginCheckCallbackFn(cookie, content):
        if "EudicWebSession" in cookie:
            return True
        return False

    def getGroups(self) -> list[tuple[str, int]]:
        """
        获取单词本分组
        :return: [(group_name,group_id)]
        """
        if self.indexSoup is None:
            return []
        elements = self.indexSoup.find_all(
            "a", class_="media_heading_a new_cateitem_click"
        )
        groups = []
        if elements:
            groups = [
                (str(el.string) if el.string else "", int(str(el["data-id"])))
                for el in elements
            ]

        logger.info(f"单词本分组:{groups}")
        self.groups = groups
        return groups

    def getTotalPage(self, groupName: str, groupId: int) -> int:
        """
        获取分组下总页数
        :param groupName: 分组名称
        :param groupId:分组id
        :return:
        """
        validation = self.validations[self.config.language.value]
        try:
            r = self.session.post(
                url=f"https://{validation.baseUrl}/StudyList/WordsDataSource",
                timeout=self.timeout,
                data={"categoryid": groupId},
            )
            records = r.json()["recordsTotal"]
            totalPages = ceil(records / 100)
            logger.info(f"该分组({groupName}-{groupId})下共有{totalPages}页")
            return totalPages
        except Exception as error:
            logger.exception(f"网络异常{error}")
            return 0

    def getWordsByPage(
        self, pageNo: int, groupName: str, groupId: str
    ) -> list[SimpleWord]:
        wordList = []
        data = {
            "columns[2][data]": "word",
            "start": pageNo * 100,
            "length": 100,
            "categoryid": int(groupId),
            "_": int(time.time()) * 1000,
        }
        validation = self.validations[self.config.language.value]
        try:
            logger.info(f"获取单词本({groupName}-{groupId})第:{pageNo + 1}页")
            r = self.session.post(
                url=f"https://{validation.baseUrl}/StudyList/WordsDataSource",
                timeout=self.timeout,
                data=data,
            )
            wl = r.json()
            wordList = [SimpleWord(word["uuid"]) for word in wl["data"]]
        except Exception as error:
            logger.exception(f"网络异常{error}")
        finally:
            logger.info(f"单词本({groupName}-{groupId})获取结果：")
            logger.info(wordList)
            return wordList

    @classmethod
    def close(cls):
        cls.session.close()
