from abc import ABC, abstractmethod
from ..dictionary.base import SimpleWord
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class QueryAPIPlatformEnum(Enum):
    APORA = 1
    YOUDAO = 2
    EUDIC = 3


@dataclass
class QueryAPIReturnType:
    """
    Dataclass representing the return type for a query to the API.
    Attributes:
        term (str): The queried term.
        definition (str): The definition of the term.
        part_of_speech (str): The part of speech of the term.
        ipa (str): The International Phonetic Alphabet representation of the term.
        original (str): The original text or source of the term.
        chinese_definition (Optional[str]): The Chinese definition of the term, if available.
        context (Optional[str]): Example context or sentence where the term is used, if available.
        collocation (Optional[list[str]]): Collections where the term is used, if available.
        term_audio_url (Optional[str]): URL to audio file of the term pronunciation, if available.
        context_audio_url (Optional[str]): URL to audio file of the context sentence, if available.
        replacing (Optional[str]): A text represent the variant of the inquiring term in context field which is used for highlighting, if available.
    """

    term: str
    definition: str
    part_of_speech: str
    ipa: str
    original: str
    chinese_definition: Optional[str]
    context: Optional[str]
    collocation: Optional[list[str]]
    term_audio_url: Optional[str]
    context_audio_url: Optional[str]
    replacing: Optional[str]
    translation: Optional[str]


def todo_empty_query_result() -> QueryAPIReturnType:
    return QueryAPIReturnType(
        term="",
        definition="",
        part_of_speech="",
        ipa="",
        original="",
        chinese_definition=None,
        context=None,
        collocation=None,
        term_audio_url=None,
        context_audio_url=None,
        replacing=None,
        translation=None,
    )


def mock_query_result() -> QueryAPIReturnType:
    return QueryAPIReturnType(
        term="liability",
        definition="Things that you owe or are responsible for, especially money you have to pay.",
        part_of_speech="noun",
        ipa="ˌlaɪəˈbɪləti",
        original="liability",
        chinese_definition="负债；债务",
        context="Keep expenses low, reduce liabilities, and diligently build a base of solid assets.",
        collocation=["liability for", "liability to do"],
        term_audio_url=None,
        context_audio_url=None,
        replacing="liability",
        translation="保持低成本，减少负债，并努力建立坚实的资产基础。",
    )


class AbstractQueryAPI(ABC):
    name: str
    """
    Query API name, must be unique.
    """

    platform: QueryAPIPlatformEnum
    """
    Query API platform enum, used to distinguish different platforms
    """

    @classmethod
    @abstractmethod
    def query(cls, term: SimpleWord) -> Optional[QueryAPIReturnType]:
        """
        查询
        :param word: 单词
        :return: 查询结果 dict(term, definition, phrase, image, sentence, BrEPhonetic, AmEPhonetic, BrEPron, AmEPron)
        """
        pass

    @classmethod
    @abstractmethod
    def close(cls):
        pass

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "name"):
            raise TypeError(
                f"Subclass {cls.__name__} must define 'name' class attribute."
            )
        if not hasattr(cls, "platform"):
            raise TypeError(
                f"Subclass {cls.__name__} must define 'name' class attribute."
            )
