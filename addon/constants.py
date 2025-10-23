VERSION = "v1.0.0"
RELEASE_URL = "https://github.com/0x0501/Apora-Dict2Anki"
VERSION_CHECK_API = "https://api.github.com/repos/lixvbnet/Dict2Anki/releases/latest"
WINDOW_TITLE = f"Apora Dict2Anki {VERSION}"
MODEL_NAME = "Apora Dict2Anki"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}

LOG_BUFFER_CAPACITY = 20  # number of log items
LOG_FLUSH_INTERVAL = 3  # seconds

# continue to use Dict2Anki 4.x model
ASSET_FILENAME_PREFIX = "MG"
MODEL_FIELDS = [
    "term",
    "definition",
    "definition_cn",
    "ipa",  # merge `us` and `uk` into ipa field
    "context",  # merge `sentence*` into context
    "image",
    "pronunciation",
    "group",
]

CARD_SETTINGS = [
    "definition_cn",
    "image",
    "pronunciation",
    "context",
]


class FieldGroup:
    def __init__(self):
        self.definition_cn = "{{definition_cn}}"
        self.image = "{{image}}"
        self.pronunciation = "{{pronunciation}}"
        self.context = "{{context}}"

    def toggleOff(self, field):
        if field not in CARD_SETTINGS:
            raise RuntimeError(
                f"Unexpected field: {field}. Must be in {CARD_SETTINGS}!"
            )
        if field == "context":
            setattr(self, field, "")
        else:
            setattr(self, field, "")

    def toString(self) -> str:
        return f"definition_cn={self.definition_cn}, image={self.image}, pronunciation={self.pronunciation}, context={self.context}"

    def __str__(self) -> str:
        return self.toString()

    def __repr__(self) -> str:
        return self.toString()


def normal_card_template_qfmt(fg: FieldGroup):
    return f"""\
<table>
    <tr>
        <td>
            <h1 class="term">{{{{term}}}}</h1>
            <span>{fg.pronunciation}</span>
            <div class="pronounce">
                <span class="phonetic">UK[{{{{ipa}}}}]</span>
            </div>
            <div class="definition">Tap To View</div>
            <div class="definition_cn"></div>
        </td>
        <td style="width: 33%;">
        </td>
    </tr>
</table>
<div class="divider"></div>

<p>{fg.context}</p>
"""


def normal_card_template_afmt(fg: FieldGroup):
    return f"""\
<table>
    <tr>
        <td>
        <h1 class="term">{{{{term}}}}</h1>
            <span>{fg.pronunciation}</span>
            <div class="pronounce">
                <span class="phonetic">UK[{{{{ipa}}}}]</span>
            </div>
            <div class="definition">{{{{definition}}}}</div>
            <div class="definition_cn">{fg.definition_cn}</div>
        </td>
        <td style="width: 33%;">
            {fg.image}
        </td>
    </tr>
</table>
<div class="divider"></div>
<p>{fg.context}</p>
</table>
"""


def backwards_card_template_qfmt(fg: FieldGroup):
    return f"""\
<table>
    <tr>
        <td>
        <h1 class="term"></h1>
            <div class="pronounce">
                <span class="phonetic">UK[Tap To View]</span>
            </div>
            <div class="definition">{{{{definition}}}}</div>
            <div class="definition_cn">{fg.definition_cn}</div>
        </td>
        <td style="width: 33%;">
            {fg.image}
        </td>
    </tr>
</table>
<div class="divider"></div>
<p>{fg.context}</p>
"""


def backwards_card_template_afmt(fg: FieldGroup):
    return normal_card_template_afmt(fg)


# Normal card template
NORMAL_CARD_TEMPLATE_NAME = "Normal"
# Backwards card template (using same AFMT and CSS with Normal card template)
BACKWARDS_CARD_TEMPLATE_NAME = "Backwards"
CARD_TEMPLATE_CSS = """\
.card {
  font-family: arial;
  font-size: 16px;
  text-align: left;
  color: #212121;
  background-color: white;
}
.pronounce {
  line-height: 30px;
  font-size: 26px;
  margin-bottom: 0;
}
.phonetic {
  font-size: 16px;
  font-family: "lucida sans unicode", arial, sans-serif;
  color: #01848f;
}
.term {
  margin-bottom: -5px;
}
.exam_type {
  margin: 1em 0 0em 0;
  color: gray;
}
.divider {
  margin: 1em 0 1em 0;
  border-bottom: 2px solid #4caf50;
}
.phrase,
.sentence {
  color: #01848f;
  padding-right: 1em;
}
img {
  max-height: 300px;
}
tr {
  vertical-align: top;
}
"""


PRON_TYPES = ["noPron", "BrEPron", "AmEPron"]


def get_pronunciation(word: dict, preferred_pron: int) -> tuple[int, bool]:
    """:return: pron_type: int, is_fallback: bool"""
    if preferred_pron == 0:
        return 0, False
    if word[PRON_TYPES[preferred_pron]]:
        return preferred_pron, False
    fallback_pron = 2 if preferred_pron == 1 else 1
    if word[PRON_TYPES[fallback_pron]]:
        return fallback_pron, True
    return 0, True


def default_image_filename(term: str) -> str:
    return f"{ASSET_FILENAME_PREFIX}-{term}.jpg"


def default_audio_filename(term: str) -> str:
    return f"{ASSET_FILENAME_PREFIX}-{term}.mp3"
