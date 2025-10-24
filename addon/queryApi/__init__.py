from . import youdao, eudict
from .base import AbstractQueryAPI
from typing import Type

QUERY_APIS: list[Type[AbstractQueryAPI]] = [youdao.API, eudict.API]
