from enum import Enum
from abc import ABC, abstractmethod

class CredentialPlatformEnum(Enum):
    """Represent credentials of different platforms"""
    NONE = 0
    YOUDAO = 1
    EUDIC = 2



class SimpleWord(ABC):
    @classmethod
    def from_values(cls, values: list[str]):
        n = len(values)
        if n == 0:
            return None
        term = values[0]
        trans = ""
        modifiedTime = 0
        bookId = 0
        bookName = ""
        if n > 1:
            trans = values[1]
        if n > 2:
            modifiedTime = int(values[2])
        if n > 3:
            bookId = int(values[3])
        if n > 4:
            bookName = values[4]
        return SimpleWord(
            term=term,
            trans=trans,
            modifiedTime=modifiedTime,
            bookId=bookId,
            bookName=bookName,
        )

    """A SimpleWord includes the term and a brief translation, as well as other metadata."""

    def __init__(self, term: str, trans="", modifiedTime=0, bookId=0, bookName=""):
        self.term = term
        self.trans = trans
        self.modifiedTime = modifiedTime
        self.bookId = bookId
        self.bookName = bookName

    def toString(self) -> str:
        return f"{self.term} {self.trans} modifiedTime={self.modifiedTime}, bookId={self.bookId}, bookName={self.bookName}"

    def __str__(self) -> str:
        # return self.toString()
        return self.term

    def __repr__(self) -> str:
        # return f'SimpleWord({self.__str__()})'
        return self.term


class AbstractDictionary(ABC):
    @staticmethod
    @abstractmethod
    def loginCheckCallbackFn(cookie: dict, content: str) -> bool:
        pass

    @abstractmethod
    def checkCookie(self, cookie: dict) -> bool:
        pass

    @abstractmethod
    def getGroups(self) -> list[tuple[str, int]]:
        pass

    @abstractmethod
    def getTotalPage(self, groupName: str, groupId: int) -> int:
        pass

    @abstractmethod
    def getWordsByPage(
        self, pageNo: int, groupName: str, groupId: str
    ) -> list[SimpleWord]:
        pass

    @classmethod
    @abstractmethod
    def close(cls):
        pass
