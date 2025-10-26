import logging
import requests
from urllib3 import Retry
from requests.adapters import HTTPAdapter
from ..constants import HEADERS
from .base import (
    AbstractQueryAPI,
    QueryAPIReturnType,
    QueryAPIPlatformEnum,
)
from typing import Optional
from ..misc import safe_load_config_from_mw


logger = logging.getLogger("dict2Anki.queryApi.eudict")
__all__ = ["API"]


class API(AbstractQueryAPI):
    name = "Apora API"
    platform = QueryAPIPlatformEnum.APORA
    timeout = 60
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    url = "https://apora.sumku.cc/api/dict"

    @classmethod
    def query(cls, term) -> Optional[QueryAPIReturnType]:
        # We need Bearer token in request header
        config = safe_load_config_from_mw()

        if len(config.aporaApiToken) == 0:
            raise RuntimeError("Apora API Token cannot be empty.")

        cls.session.headers["Authorization"] = f"Bearer {config.aporaApiToken}"

        queryResult = None

        payload = {
            "inquire": term.term,
        }

        if config.contextSpeaking:
            payload["speech"] = "tts_sentence"
        if config.termSpeaking:
            payload["speech"] = "tts_words"
        if config.USSpeaking:
            payload["variant"] = "US"
        if config.GreatBritainSpeaking:
            payload["variant"] = "GB"

        try:
            response = cls.session.post(cls.url, json=payload, timeout=cls.timeout)
            logger.debug(
                f"code:{response.status_code}- word:{term.term} text:{response.text}"
            )

            response_json = response.json()

            logger.info(response_json)

            response_data_json = response_json["data"]

            if (
                response.status_code == 200
                and response_json["success"]
                and response_data_json
            ):
                audio_download_link = None
                # for highlight term in context
                replacing = None

                if config.contextSpeaking or config.termSpeaking:
                    # we need to create audio download link
                    filename_tag = response_data_json["fileNameTag"]
                    audio_download_link = f"https://apora.sumku.cc/api/audio/{config.aporaApiToken}/{filename_tag}.wav"

                if config.enableContext:
                    replacing = response_data_json["replacing"]

                # successfully get dict data from Apora
                queryResult = QueryAPIReturnType(
                    term=term.term,
                    definition=response_data_json["meaning"],
                    part_of_speech=response_data_json["partOfSpeech"],
                    original=response_data_json["original"],
                    chinese_definition=response_data_json["chineseMeaning"],
                    ipa=response_data_json["ipa"],
                    context=response_data_json["context"],
                    collocation=None,
                    context_audio_url=audio_download_link,
                    term_audio_url=audio_download_link,
                    replacing=replacing,
                )
            else:
                raise Exception(
                    f"Get dict data for word: {term.term} failed, reason: {response_json['message']}"
                )

        except Exception as e:
            logger.exception(e)
        finally:
            logger.debug(queryResult)
            return queryResult

    @classmethod
    def close(cls):
        cls.session.close()
