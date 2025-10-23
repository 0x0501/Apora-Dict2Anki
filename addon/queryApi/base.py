from abc import ABC, abstractmethod
from ..dictionary.base import SimpleWord


class AbstractQueryAPI(ABC):
    @classmethod
    @abstractmethod
    def query(cls, word: SimpleWord) -> dict:
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
