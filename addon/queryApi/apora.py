import logging
import requests
from urllib3 import Retry
from requests.adapters import HTTPAdapter
from ..constants import HEADERS
from .base import (
    AbstractQueryAPI,
    QueryAPIReturnType,
    todo_empty_query_result,
    QueryAPIPlatformEnum,
)
from ..dictionary.base import SimpleWord
from ..misc import safe_load_config_from_mw


logger = logging.getLogger("dict2Anki.queryApi.eudict")
__all__ = ["API"]


class API(AbstractQueryAPI):
    name = "Apora API"
    platform = QueryAPIPlatformEnum.APORA
    timeout = 10
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    url = "https://apora.sumku.cc/api/dict"

    @classmethod
    def query(cls, term) -> QueryAPIReturnType:
        # We need Bearer token in request header
        config = safe_load_config_from_mw()

        if len(config.aporaApiToken) == 0:
            raise RuntimeError("Apora API Token cannot be empty.")

        cls.session.headers["Authorization"] = f"Bearer {config.aporaApiToken}"

        # TODO: request dict

        return todo_empty_query_result()

    @classmethod
    def close(cls):
        cls.session.close()
