import logging
import requests
from urllib3 import Retry
from requests.adapters import HTTPAdapter
from ..constants import HEADERS
from .base import (
    AbstractQueryAPI,
    QueryAPIReturnType,
    mock_query_result,
    QueryAPIPlatformEnum,
)
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

        queryResult = mock_query_result()

        return queryResult
        # payload = {
        #     "inquire": "liabilities",
        #     "fullText": "Keep expenses low, reduce liabilities, and diligently build a base of solid assets.",
        # }

        # try:
        #     response = cls.session.post(cls.url, json=payload, timeout=cls.timeout)
        #     logger.debug(
        #         f"code:{response.status_code}- word:{term.term} text:{response.text}"
        #     )

        #     response_json = response.json()

        #     print(response_json)

        #     response_data_json = response_json["data"]

        #     if (
        #         response.status_code == 200
        #         and response_json["success"]
        #         and response_data_json
        #     ):
        #         # successfully get dict data from Apora
        #         queryResult = QueryAPIReturnType(
        #             term=term.term,
        #             definition=response_data_json["meaning"],
        #             part_of_speech=response_data_json["partOfSpeech"],
        #             original=response_data_json["original"],
        #             chinese_definition=response_data_json["chineseMeaning"],
        #             ipa=response_data_json["ipa"],
        #             context=None,
        #             collocation=None,
        #             context_audio_url=None,
        #             term_audio_url=None,
        #         )
        #     else:
        #         raise Exception(
        #             f"Get dict data for word: {term.term} failed, reason: {response_json['message']}"
        #         )

        # except Exception as e:
        #     logger.exception(e)
        # finally:
        #     logger.debug(queryResult)
        #     return queryResult

    @classmethod
    def close(cls):
        cls.session.close()
