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
from ..exceptions import BalanceInsufficientException, QueryAPIError


logger = logging.getLogger("Apora dict2Anki.queryApi.eudict")
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
        config = safe_load_config_from_mw()
        if not config.aporaApiToken:
            raise RuntimeError("Apora API Token cannot be empty.")

        cls.session.headers["Authorization"] = f"Bearer {config.aporaApiToken}"

        payload = {
            "inquire": term.term,
            "contextDifficulty": config.contextDifficulty,
            "language": config.language.value,
        }

        if config.contextSpeaking:
            payload["speech"] = "tts_sentence"
        elif config.termSpeaking:  # 注意：这里用 elif，避免同时设置
            payload["speech"] = "tts_words"

        if config.USSpeaking:
            payload["variant"] = "US"
        elif config.GreatBritainSpeaking:
            payload["variant"] = "GB"

        try:
            response = cls.session.post(cls.url, json=payload, timeout=cls.timeout)
            logger.debug(
                "code:%d - word:%s - text:%s",
                response.status_code,
                term.term,
                response.text,
            )

            # 1. parse json from request body
            response_json: dict = response.json()
            logger.info("API response: %s", response_json)

            if "data" not in response_json:
                error = response_json.get("error")
                if error is not None:
                    error_str = str(error)
                    if "Insufficient balance" in error_str:
                        raise BalanceInsufficientException(
                            "Insufficient balance to perform the query."
                        )
                    else:
                        raise QueryAPIError(f"API error: {error_str}")
                else:
                    raise QueryAPIError(
                        "Server returned no 'data' and no 'error' field."
                    )

            response_data = response_json["data"]

            # 2. check query result, success should be Truthy
            if not response_json.get("success", False) or not response_data:
                message = response_json.get("message", "Unknown reason")
                raise QueryAPIError(f"Query failed for '{term.term}': {message}")

            audio_download_link = None
            if config.contextSpeaking or config.termSpeaking:
                filename_tag = response_data.get("fileNameTag")
                if filename_tag:
                    audio_download_link = f"https://apora.sumku.cc/api/audio/{config.aporaApiToken}/{filename_tag}.wav"

            replacing = response_data.get("replacing") if config.enableContext else None

            queryResult = QueryAPIReturnType(
                term=term.term,
                definition=response_data["meaning"],
                part_of_speech=response_data["partOfSpeech"],
                original=response_data["original"],
                chinese_definition=response_data["chineseMeaning"],
                ipa=response_data["ipa"],
                context=response_data["context"],
                collocation=None,
                context_audio_url=audio_download_link,
                term_audio_url=audio_download_link,
                replacing=replacing,
            )

            logger.debug("Query result: %s", queryResult)
            return queryResult

        except requests.RequestException as e:
            # network error
            logger.exception("Network error during query for term: %s", term.term)
            raise QueryAPIError(f"Network error: {e}") from e

    @classmethod
    def close(cls):
        cls.session.close()
