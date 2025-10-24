from . import youdao, eudict
from .base import AbstractDictionary
from typing import Type

DICTIONARIES: tuple[Type[AbstractDictionary], ...] = (
    youdao.Youdao,
    eudict.Eudict,
)
