from .base import QueryAPIReturnType
from ..misc import PronunciationVariantEnum


def get_pronunciation(
    _word: QueryAPIReturnType, preferred_pron: PronunciationVariantEnum
) -> tuple[PronunciationVariantEnum, bool]:
    """:return: pron_type: int, is_fallback: bool"""
    return preferred_pron, False
