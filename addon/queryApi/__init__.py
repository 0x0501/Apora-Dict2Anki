from . import apora
from .base import AbstractQueryAPI
from typing import Type

QUERY_APIS: list[Type[AbstractQueryAPI]] = [apora.API]
