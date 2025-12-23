from .constants import (
    BACKWARDS_CARD_TEMPLATE_NAME,
    CARD_TEMPLATE_CSS,
    MODEL_FIELDS,
    NORMAL_CARD_TEMPLATE_NAME,
    FieldGroup,
    backwards_card_template_afmt,
    backwards_card_template_qfmt,
    normal_card_template_afmt,
    normal_card_template_qfmt,
)
import logging
from aqt import mw
from anki.decks import DeckDict
from anki.notes import Note
from anki.models import NotetypeDict
from .misc import ConfigType, PronunciationVariantEnum
from .queryApi.base import QueryAPIReturnType
from typing import Optional, Union
from .utils import swap_positions_with_list, default_audio_filename
from pathlib import Path


logger = logging.getLogger("Apora dict2Anki.noteManager")


def getDeckList() -> list[str]:
    if mw.col is None:
        raise Exception("Collection is not available")
    return [deck["name"] for deck in mw.col.decks.all()]


def getWordsByDeck(deckName: str) -> list[str]:
    if mw.col is None:
        raise Exception("Collection is not available")
    notes = mw.col.find_notes(f'deck:"{deckName}"')
    words = []
    for nid in notes:
        note = mw.col.get_note(nid)
        note_type = note.note_type()

        if note_type is None:
            raise Exception("note_type is none")

        if (
            note_type.get("name", "").lower().startswith("apora-dict2anki")
            and note["term"]
        ):
            words.append(note["term"])
    return words


def getNoteIDsOfWords(wordList: list[str], deckName: str) -> list:
    if mw.col is None:
        raise Exception("mw.col is none")
    notes = []
    for word in wordList:
        note = mw.col.find_notes(f'deck:"{deckName}" term:"{word}"')
        if note:
            notes.append(note[0])
    return notes


def getOrCreateDeck(deckName: str, model: NotetypeDict):
    if mw.col is None:
        raise Exception("mw.col is none")

    deck_id = mw.col.decks.id(deckName)

    if deck_id is None:
        raise Exception("deck_id is none.")

    deck = mw.col.decks.get(deck_id)

    if deck is None:
        raise Exception("deck is none")

    mw.col.decks.select(deck["id"])
    mw.col.decks.save(deck)

    if mw.col.models is None:
        raise Exception("mw.col.models is none")

    mw.col.models.set_current(model)
    model["did"] = deck["id"]
    mw.col.models.save(model)
    mw.reset()

    return deck


def getOrCreateModel(
    modelName: str, disableContext=False, recreate=False
) -> tuple[NotetypeDict, bool, bool]:
    """
    Create Note Model (Note Type).

    :param remapping: Swap (map) fields order.

    :return tuple[NotetypeDict, bool, bool]: (model, newCreated, fieldsUpdated)
    """

    if mw.col is None:
        raise Exception("mw.col is none")

    model = mw.col.models.by_name(modelName)
    if model:
        if not recreate:
            updated = mergeModelFields(model)
            return model, False, updated
        else:  # Dangerous action!!!  It would delete model, AND all its cards/notes!
            logger.warning(f"Force deleting and recreating model {modelName}")
            mw.col.models.rem(model)

    logger.info(f"Creating model {modelName}")
    newModel = mw.col.models.new(modelName)

    fields = MODEL_FIELDS

    if disableContext:
        # swap fields order
        fields = swap_positions_with_list(MODEL_FIELDS, [["context", "term"]])

    for field in fields:
        mw.col.models.addField(newModel, mw.col.models.new_field(field))
    return newModel, True, True


def getOrCreateCardTemplate(
    modelObject: NotetypeDict, cardTemplateName, qfmt, afmt, css, add=True
):
    """Create Card Template (Card Type)"""
    logger.info(f"Add card template {cardTemplateName}")
    existingCardTemplate = modelObject["tmpls"]

    if mw.col is None:
        raise Exception("mw.col is none")

    if cardTemplateName in [t.get("name") for t in existingCardTemplate]:
        logger.info(f"[Skip] Card Type '{cardTemplateName}' already exists.")
        return
    cardTemplate = mw.col.models.new_template(cardTemplateName)
    cardTemplate["qfmt"] = qfmt
    cardTemplate["afmt"] = afmt
    modelObject["css"] = css
    mw.col.models.addTemplate(modelObject, cardTemplate)
    if add:
        mw.col.models.add(modelObject)
    else:
        mw.col.models.save(modelObject)


def getOrCreateNormalCardTemplate(modelObject: NotetypeDict, fg: FieldGroup):
    """Create Normal Card Template (Card Type)"""
    qfmt = normal_card_template_qfmt(fg)
    afmt = normal_card_template_afmt(fg)
    getOrCreateCardTemplate(
        modelObject, NORMAL_CARD_TEMPLATE_NAME, qfmt, afmt, CARD_TEMPLATE_CSS, add=True
    )


def getOrCreateBackwardsCardTemplate(modelObject: NotetypeDict, fg: FieldGroup):
    """Create Backwards Card Template (Card Type) to existing Dict2Anki Note Type"""
    qfmt = backwards_card_template_qfmt(fg)
    afmt = backwards_card_template_afmt(fg)
    getOrCreateCardTemplate(
        modelObject,
        BACKWARDS_CARD_TEMPLATE_NAME,
        qfmt,
        afmt,
        CARD_TEMPLATE_CSS,
        add=False,
    )


def deleteBackwardsCardTemplate(modelObject: NotetypeDict, backwardsTemplateObject):
    """Delete Backwards Card Template (Card Type) from existing Dict2Anki Note Type"""

    if mw.col is None:
        raise Exception("mw.col is none")

    mw.col.models.remove_template(modelObject, backwardsTemplateObject)
    mw.col.models.save(modelObject)


def checkModelFields(modelObject: NotetypeDict) -> tuple[bool, set, set]:
    """Check if model fields are as expected. :return: (ok, unknown_fields, missing_fields)"""
    current_fields = [f["name"] for f in modelObject["flds"]]
    expected_fields = MODEL_FIELDS

    set_current = set(current_fields)
    set_expected = set(expected_fields)
    if set_current == set_expected:
        return True, set(), set()
    else:
        unknown_fields = set_current - set_expected
        missing_fields = set_expected - set_current
        return False, unknown_fields, missing_fields


def mergeModelFields(modelObject: NotetypeDict) -> bool:
    """Merge model fields. Only need to do updates when there are missing fields. return: updated"""
    ok, unknown_fields, missing_fields = checkModelFields(modelObject)
    if ok or (not missing_fields):
        return False

    if mw.col is None:
        raise Exception("mw.col is none")

    logger.warning(f"unknown fields: {unknown_fields}")
    logger.warning(f"missing fields: {missing_fields}")
    logger.info("Merge model fields...")
    fields = modelObject["flds"]
    # field_map = {f["name"]: (f["ord"], f) for f in fields}
    field_map = mw.col.models.field_map(modelObject)

    fields.clear()
    logger.info(f"step 1. add MODEL_FIELDS: {MODEL_FIELDS}")
    for f_name in MODEL_FIELDS:
        if f_name in field_map:
            index, field = field_map[f_name]
        else:
            field = mw.col.models.new_field(f_name)
        fields.append(field)
    logger.info(f"step 2. add unknown_fields: {unknown_fields}")
    for f_name in unknown_fields:
        index, field = field_map[f_name]
        fields.append(field)
    mw.col.models.save(modelObject)
    return True


def checkModelCardTemplates(modelObject: NotetypeDict, fg: FieldGroup) -> bool:
    """Check if model card templates are as expected"""
    for tmpl in modelObject["tmpls"]:
        tmpl_name = tmpl["name"]
        logger.info(f"Found card template '{tmpl_name}'")
        if tmpl_name == NORMAL_CARD_TEMPLATE_NAME:
            if tmpl["qfmt"] != normal_card_template_qfmt(fg) or tmpl[
                "afmt"
            ] != normal_card_template_afmt(fg):
                logger.info(f"Changes detected in template '{tmpl_name}'")
                return False
        elif tmpl_name == BACKWARDS_CARD_TEMPLATE_NAME:
            if tmpl["qfmt"] != backwards_card_template_qfmt(fg) or tmpl[
                "afmt"
            ] != backwards_card_template_afmt(fg):
                logger.warning(f"Changes detected in template '{tmpl_name}'")
                return False
    return True


def checkModelCardCSS(modelObject: NotetypeDict) -> bool:
    """Check if model CSS are as expected"""
    current_css = modelObject["css"]
    expected_css = CARD_TEMPLATE_CSS
    if current_css == expected_css:
        return True
    else:
        logger.warning("Changes detected in card CSS")
        return False


def resetModelCardTemplates(modelObject: NotetypeDict, fg: FieldGroup):
    """Reset Card Templates to default"""
    for tmpl in modelObject["tmpls"]:
        tmpl_name = tmpl["name"]
        if tmpl_name == NORMAL_CARD_TEMPLATE_NAME:
            logger.info(f"Reset card template '{NORMAL_CARD_TEMPLATE_NAME}'")
            tmpl["qfmt"] = normal_card_template_qfmt(fg)
            tmpl["afmt"] = normal_card_template_afmt(fg)
        elif tmpl_name == BACKWARDS_CARD_TEMPLATE_NAME:
            logger.info(f"Reset card template '{BACKWARDS_CARD_TEMPLATE_NAME}'")
            tmpl["qfmt"] = backwards_card_template_qfmt(fg)
            tmpl["afmt"] = backwards_card_template_afmt(fg)
    logger.info("Reset CSS")
    modelObject["css"] = CARD_TEMPLATE_CSS
    logger.info("Save changes")

    if mw.col is None:
        raise Exception("mw.col is none")

    mw.col.models.save(modelObject)


def setNoteFieldValue(
    note: Note, key: str, value: str, isNewNote: bool, overwrite: bool
) -> bool:
    """set note field value. :return isWritten"""

    if not value:
        return False
    if isNewNote or overwrite:
        note[key] = value
        return True
    if not note[key]:  # field value of the Existing Note is missing
        note[key] = value
        return True
    return False


def appendTagToNote(note: Note, tag: Union[str, list[str]]):
    """Append tag into note"""
    if len(tag) > 0:
        if isinstance(tag, str):
            note.add_tag(tag)
        else:
            note.set_tags_from_str(" ".join(tag))


def loadAssetsIntoCollectionMedia():
    if mw.col is None:
        raise Exception("mw.col is none")

    current_path = Path(__file__).absolute().parent

    assets_path = current_path.joinpath("assets")

    media = mw.col.media

    for p in assets_path.iterdir():
        media.add_file(p.as_posix())
    pass


def addNoteToDeck(
    deck: Optional[DeckDict],
    model: Optional[NotetypeDict],
    config: ConfigType,
    word: QueryAPIReturnType,
    pronunciationVariant: PronunciationVariantEnum,
    existing_note: Optional[Note],
    overwrite=False,
):
    """
    Add note
    :param deck: deck
    :param model: model
    :param config: currentConfig
    :param word: (dict) query result of a word
    :param whichPron:
    :param existing_note: if not None, then do not create new note
    :param overwrite: True to overwrite existing note, and False to fill missing values only. (Only relevant when
                        'existing_note' is not None.
    :return: None
    """
    if not word:
        logger.warning(f"查询结果{word} 异常，忽略")
        return

    if mw.col is None:
        raise Exception("mw.col is none")

    isNewNote = existing_note is None
    if isNewNote:
        if not model or not deck:
            logger.error("Cannot create new note: model or deck is missing")
            return
        model["did"] = deck["id"]
        note = Note(mw.col, model)  # create new note
    else:
        note = existing_note  # existing note

    term = word.term
    setNoteFieldValue(note, "term", term, isNewNote, overwrite)
    # note['term'] = term

    # ================================== Required fields ==================================
    # 1. Required fields are always included in Anki cards and cannot be toggled off
    # 2. Always add to note if it has a value

    # group (bookName)
    #!TODO: For now disable group info, we'll consider this in the future
    # if word["bookName"]:
    #     key, value = "group", word["bookName"]
    #     setNoteFieldValue(note, key, value, isNewNote, overwrite)
    #     # note['group'] = word['bookName']

    # exam_type
    #!TODO: For now disable exam_type info, we'll consider this in the future
    # if word["exam_type"]:  # [str]
    #     key, value = "exam_type", " / ".join(word["exam_type"])
    #     setNoteFieldValue(note, key, value, isNewNote, overwrite)
    #     # note['exam_type'] = " / ".join(word['exam_type'])

    # International Phonetic Alphabet (IPA)
    if word.ipa:
        setNoteFieldValue(note, "ipa", word.ipa, isNewNote, overwrite)
        # note['us'] = word['AmEPhonetic']

    if word.part_of_speech:
        setNoteFieldValue(
            note, "part_of_speech", word.part_of_speech, isNewNote, overwrite
        )
        if config.enableAddPartOfSpeechToTag:
            appendTagToNote(note, word.part_of_speech)

    # definition

    if word.definition:
        setNoteFieldValue(note, "definition", word.definition, isNewNote, overwrite)

    # ================================== Optional fields ==================================
    # 1. Ignore "query settings"
    # 2. Always add to note if it has a value
    # 3. Toggle visibility by dynamically updating card template

    # definition_cn
    if word.chinese_definition and config.enableChineseDefinition:
        setNoteFieldValue(
            note, "definition_cn", word.chinese_definition, isNewNote, overwrite
        )

    # image
    #!TODO: For now disable image, we'll consider this in the future
    # if word["image"]:
    #     imageFilename = default_image_filename(term)
    #     key, value = "image", f'<div><img src="{imageFilename}" /></div>'
    #     setNoteFieldValue(note, key, value, isNewNote, overwrite)
    # note['image'] = f'<div><img src="{imageFilename}" /></div>'

    # pronunciation
    if pronunciationVariant is not PronunciationVariantEnum.NONE:
        pronFilename = default_audio_filename(
            term, "wav"
        )  # For now, use `.wav` as default, this should be flexible
        key, value = "pronunciation", f"[sound:{pronFilename}]"
        setNoteFieldValue(note, key, value, isNewNote, overwrite)
        # note['pronunciation'] = f"[sound:{pronFilename}]"

    # phrase
    #!TODO: For now disable collocation, we'll consider this in the future
    # if word.collocation:
    #     for i, phrase_tuple in enumerate(word["phrase"][:3]):  # at most 3 phrases
    #         key, value = f"phrase{i}", phrase_tuple[0]
    #         setNoteFieldValue(note, key, value, isNewNote, overwrite)
    #         key, value = f"phrase_explain{i}", phrase_tuple[1]
    #         setNoteFieldValue(note, key, value, isNewNote, overwrite)
    #         key, value = f"pplaceHolder{i}", "Tap To View"
    #         setNoteFieldValue(note, key, value, isNewNote, overwrite)

    # sentence
    if word.context and config.enableContext:
        if config.enableTermHighlight and word.replacing:
            # highlight term in the context

            # if replacing field is not none, replace it
            highlighted_context = word.context.replace(
                word.replacing,
                f'<span style="font-weight: bold; color: #4096ff;">{word.replacing}</span>',
            )
            setNoteFieldValue(
                note, "context", highlighted_context, isNewNote, overwrite
            )
        else:
            setNoteFieldValue(note, "context", word.context, isNewNote, overwrite)

    # if context translation enabled
    if word.translation:
        setNoteFieldValue(note, "translation", word.translation,isNewNote,overwrite)

    if isNewNote:
        mw.col.addNote(note)
        logger.info(f"添加笔记{term}")
    else:
        mw.col.update_note(note)
        logger.info(f"更新笔记{term}")
