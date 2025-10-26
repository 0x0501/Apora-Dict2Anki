VERSION = "v1.0.0"
RELEASE_URL = "https://github.com/0x0501/Apora-Dict2Anki"
VERSION_CHECK_API = "https://api.github.com/repos/lixvbnet/Dict2Anki/releases/latest"
WINDOW_TITLE = f"Apora Dict2Anki {VERSION}"
MODEL_NAME = "Apora Dict2Anki"
MODEL_NAME_DISABLED_CONTEXT = "Apora Dick2Anki (Disabled Context)"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}

LOG_BUFFER_CAPACITY = 20  # number of log items
LOG_FLUSH_INTERVAL = 3  # seconds

# continue to use Dict2Anki 4.x model
ASSET_FILENAME_PREFIX = "APORA"

# Field name cannot be duplicate, so we use tuple instead of list
MODEL_FIELDS = [
    "context",
    "term",
    "ipa",  # merge `us` and `uk` into ipa field
    "image",
    "definition",
    "definition_cn",
    "part_of_speech",
    "pronunciation",
    "translation",  # Chinese translation for contextS
    "extra",  # Extra info use to recall the card
    "group",
]

CARD_SETTINGS = [
    "termSpeaking",
    "contextSpeaking",
    "enableContext",
    "GreatBritainSpeaking",
    "USSpeaking",
    "disableSpeaking",
]


class FieldGroup:
    def __init__(self):
        self.definition_cn = "{{definition_cn}}"
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
        return f"definition_cn={self.definition_cn}, pronunciation={self.pronunciation}, context={self.context}"

    def __str__(self) -> str:
        return self.toString()

    def __repr__(self) -> str:
        return self.toString()


def normal_card_template_qfmt(fg: FieldGroup):
    """QA Card Front Template (Question)."""
    return """\
<div id='app'>
    <div class='header'>
        <img src="_apora_icon.png" alt="apora_logo" width="30px" />
        <a href="https://apora.sumku.cc">Apora Dict</a>
    </div>
    <div class='mnemonic'>{{image}}</div>
    <div class="card-wrapper">
        <p class='sentence'>
            {{context}}
        </p>
    </div>
    <div id="phrase-pronunciation">
        <p>{{pronunciation}}</p>
    </div>
    {{#Tags}}
    <div class="tags-group">
        <span class="font-pixelify">Info:</span>
    </div>
    {{/Tags}}
</div>

<script>
    (function () {
        const tagsMeta = "{{Tags}}".split(" ");

        const tagElements = tagsMeta
            .map(function (val) {
                const classList = ["tag-item"];

                classList.push(val);

                return `<span class='${classList.join(" ")}'>${val}</span>`;
            })
            .join("");

        if ($(".tags-group")[0] === undefined) return;

        $(".tags-group")[0].innerHTML += tagElements;
    })();

</script>
"""


def normal_card_template_afmt(fg: FieldGroup):
    """QA Card Back Template (Answer)."""
    return """\
<div id="app">
    <div class='header'>
        <img src="_apora_icon.png" alt="apora_logo" width="30px" />
        <a href="https://apora.sumku.cc">Apora Dict</a>
    </div>
    <div class="mnemonic">{{image}}</div>
    <div class="card-wrapper">
        <div class="sentence">
            <p>{{context}}</p>
        </div>
    </div>
    <hr id="answer" />
    <div class="answer">
        <p id="phrase">{{term}} {{#ipa}}<span class="phonetic">{{ipa}}</span>{{/ipa}}
            {{#pronunciation}}
            <svg class="icon" id="play-phrase" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512">
                <path
                    d="M533.6 32.5C598.5 85.3 640 165.8 640 256s-41.5 170.8-106.4 223.5c-10.3 8.4-25.4 6.8-33.8-3.5s-6.8-25.4 3.5-33.8C557.5 398.2 592 331.2 592 256s-34.5-142.2-88.7-186.3c-10.3-8.4-11.8-23.5-3.5-33.8s23.5-11.8 33.8-3.5zM473.1 107c43.2 35.2 70.9 88.9 70.9 149s-27.7 113.8-70.9 149c-10.3 8.4-25.4 6.8-33.8-3.5s-6.8-25.4 3.5-33.8C475.3 341.3 496 301.1 496 256s-20.7-85.3-53.2-111.8c-10.3-8.4-11.8-23.5-3.5-33.8s23.5-11.8 33.8-3.5zm-60.5 74.5C434.1 199.1 448 225.9 448 256s-13.9 56.9-35.4 74.5c-10.3 8.4-25.4 6.8-33.8-3.5s-6.8-25.4 3.5-33.8C393.1 284.4 400 271 400 256s-6.9-28.4-17.7-37.3c-10.3-8.4-11.8-23.5-3.5-33.8s23.5-11.8 33.8-3.5zM301.1 34.8C312.6 40 320 51.4 320 64V448c0 12.6-7.4 24-18.9 29.2s-25 3.1-34.4-5.3L131.8 352H64c-35.3 0-64-28.7-64-64V224c0-35.3 28.7-64 64-64h67.8L266.7 40.1c9.4-8.4 22.9-10.4 34.4-5.3z" />
            </svg>{{/pronunciation}}
        </p>
        {{#definition}}<p id="definition">{{definition}}</p>{{/definition}}
    </div>

    <div class="region-container">
        {{#definition_cn}}
        <div class="chinese-def region tappable" data-active="false">
            <p class="font-pixelify region-title">Chinese Definition</p>
            <p class="region-content">{{definition_cn}}</p>
        </div>
        {{/definition_cn}}

        {{#translation}}
        <div class="translation region tappable" data-active="false">
            <p class="font-pixelify region-title">Translation</p>
            <p class="region-content">{{translation}}</p>
        </div>
        {{/translation}}

        {{#extra}}
        <div class="extra-info region">
            <p class="font-pixelify region-title">Extra</p>
            <p class="region-content">{{extra}}</p>
        </div>
        {{/extra}}
    </div>
    {{#Tags}}
    <div class="tags-group">
        <span class="font-pixelify">Info:</span>
    </div>
    {{/Tags}}
    <div class="invisible" id="phrase-pronunciation">
        <p>{{pronunciation}}</p>
    </div>
</div>

<script>
    (function () {
        // turn on the anki legacy player button (rendered by SVG)
        var isLegacyPlayer = true;
        var tagsMeta = "{{Tags}}".split(" ");
        var playPhrase = $("#play-phrase")[0];
        var moreExample = $(".extra-info p")[0];
        var moreExampleMeta = $(".extra-info ul")[0];

        if ($("#phrase-pronunciation a")[0]) {
            playPhrase.onclick = $("#phrase-pronunciation a")[0].onclick;
        }

        // replace audio player
        if (isLegacyPlayer) {
            $("#phrase-pronunciation")[0].classList.remove("hidden");
        }

        function loadTags() {
            var tagElements = tagsMeta
                .map(function (val) {
                    var classList = ["tag-item"];

                    classList.push(val);

                    return `<span class='${classList.join(" ")}'>${val}</span>`;
                })
                .join("");

            if ($(".tags-group")[0] === undefined) return;

            $(".tags-group")[0].innerHTML += tagElements;
        }

        function addInteractionToRegions() {
            var chineseMeaningRegion = $(".chinese-def")[0];
            var sentenceTranslationRegion = $(".translation")[0];

            if (chineseMeaningRegion) {
                var chineseMeaningRegionContentElement = $('.chinese-def .region-content')[0];

                var chineseMeaningRegionContent = chineseMeaningRegionContentElement.innerHTML;

                var activeStatus = chineseMeaningRegion.dataset.active;

                if (activeStatus === "false") {
                    chineseMeaningRegionContentElement.innerText = "👉 Reveal Chinese Def."
                }

                chineseMeaningRegion.addEventListener('click', (e) => {
                    const status = chineseMeaningRegion.dataset.active;

                    if (status === "false") {
                        chineseMeaningRegion.dataset.active = "true";
                        chineseMeaningRegionContentElement.innerHTML = chineseMeaningRegionContent;
                    } else {
                        chineseMeaningRegion.dataset.active = "false";
                        chineseMeaningRegionContentElement.innerText = "👉 Reveal Chinese Def."
                    }
                })

            }

            if (sentenceTranslationRegion) {
                var sentenceTranslationRegionContentElement = $('.translation .region-content')[0];

                var sentenceTranslationRegionContent = sentenceTranslationRegionContentElement.innerHTML;

                var activeStatus = sentenceTranslationRegion.dataset.active;

                if (activeStatus === "false") {
                    sentenceTranslationRegionContentElement.innerText = "👉 Reveal Chinese Trans."
                }

                sentenceTranslationRegion.addEventListener('click', (e) => {
                    const status = sentenceTranslationRegion.dataset.active;

                    if (status === "false") {
                        sentenceTranslationRegion.dataset.active = "true";
                        sentenceTranslationRegionContentElement.innerHTML = sentenceTranslationRegionContent;
                    } else {
                        sentenceTranslationRegion.dataset.active = "false";
                        sentenceTranslationRegionContentElement.innerText = "👉 Reveal Chinese Trans."
                    }
                })

            }
        }

        function initPhonetics() {
            var phoneticsElement = $(".phonetic")[0];

            if (phoneticsElement) {
                var phoneticsContent = phoneticsElement.innerText;

                // check whether there're slashes around IPA
                if (!phoneticsContent.startsWith("/") && !phoneticsContent.endsWith("/")) {
                    phoneticsElement.innerText = `/${phoneticsContent}/`
                }
            }
        }

        loadTags();
        initPhonetics();
        addInteractionToRegions();
    })()
</script>
"""


def backwards_card_template_qfmt(fg: FieldGroup):
    """Reversed QA Card Front Template (Question)."""
    return f"""\
<table>
    <tr>
        <td>
        <h1 class="term"></h1>
            <div class="pronounce">
                <span class="phonetic">UK[Tap To View]</span>
            </div>
            <div class="definition">{{{{Definition}}}}</div>
            <div class="definition_cn">{fg.definition_cn}</div>
        </td>
    </tr>
</table>
<div class="divider"></div>
<p>{fg.context}</p>
"""


def backwards_card_template_afmt(fg: FieldGroup):
    """Reversed QA Card Back Template (Answer). Same as Normal QA Back."""
    return normal_card_template_afmt(fg)


# Normal card template
NORMAL_CARD_TEMPLATE_NAME = "Normal"
# Backwards card template (using same AFMT and CSS with Normal card template)
BACKWARDS_CARD_TEMPLATE_NAME = "Backwards"
CARD_TEMPLATE_CSS = """\
.card {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  font-size: 20px;
  text-align: center;
  color: black;
	background-color: #ffffff;
}

body {
	margin: 0;
}

@font-face {
    font-family: "Pixelify Sans";
    font-style: normal;
    src: url("_PixelifySans-Regular.ttf");
}

.font-pixelify {
	font-family: "Pixelify Sans";
}

#app {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 0 1.5rem;
}

#app > * {
	width: 100%;
}

.header {
	text-align: left;
	display: flex;
	align-items: center;
	gap: 0.5rem;
	margin-top: 1rem;
	margin-bottom: 1rem;
	margin-left: 0.5rem;
	margin-right: 0.5rem;
}

.header a {
	font-size: 16pt;
	font-weight: bold;
	text-decoration: none;
	color: blank;
	font-family: "Pixelify Sans"
}

.nightMode .header > a {
	color: #9f84b8 !important;
}

.header a:link,
.header a:visited,
.header a:hover,
.header a:active {
  color: black;
}

.card-wrapper {
	background-color: #f9f0ff;
	border-radius: 4px;
}

.nightMode .card-wrapper {
	border-bottom: 3px solid #9f84b8;
	border-radius: 0;
	color: #bfbfbf;
	background: transparent;
}

#definition {
	color: #1677ff;
	text-align: left;
}

.region-container {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.region {
	border-radius: 4px;
	font-size: 12pt;
	text-align: left;
	color: #595959;
	min-height: 80px;
}

.region > p {
	margin: .5rem 1rem;
}

.nightMode .region {
	color: #b8b7b4;
}

.nightMode .chinese-def {
	background-color: #3f7559;
}

.nightMode .translation {
	background-color: #805276;
}

.nightMode .extra-info {
	background-color: #8c8674;
}

.chinese-def {
	background-color: #d2fae5;
}

.chinese-def > p {
	font-size: 12pt;
}

.translation {
	background-color: #fff0fc;
}


#phrase-pronunciation p {
	margin: 20px 0 0 0;
}

#phonetic {
	margin: 0;
	font-weight: bold;
	color: #1677ff;
}

#phonetic.reversed {
	color: #9254de;
}

.phonetic {
	margin: 0px 0px 0px 10px;
	color: #1677ff;
}

.icon {
	width: 25px;
	height: auto;
	margin: 0 10px;
	cursor: pointer;
	fill:  #595959;
}

.answer span {
	display: inline-flex;
	align-items: center;
	justify-content: center;
}

.nightMode .mnemonic {
	background-color: transparent;
}

.mnemonic {
	background-color: #f7f7f7;
	border-radius: 4px;
	margin-bottom: 10px;
}

.mnemonic img {
	max-width: 300px !important;
	height: auto;
	margin: 0.5rem;
}

@media screen and (min-width: 700px) {
	.mnemonic img {
		max-width: 500px !important;
	}
}

.nightMode hr#answer {
	background-color: #9f84b8 !important;
}

hr#answer {
	background-color: #d3adf7 !important;
	height: 3px;
	outline: none;
	border: none;
}

.sentence {
	padding: 0 20px;
	text-align: left;
}

.sentence.reversed {
	font-weight: bold;
	color: #4096ff;
}

.extra-info {
	background-color: #fffaf0;
	border: none;
}

.answer {
	text-align: left;
}

#phrase {
	display: flex;
	align-items: center;
}

.region-title {
	font-size: 14pt !important;
	font-weight: bold;
}

.answer #phrase {
	color: red;
	font-weight: bold;
}

.invisible {
	display: none;
}

.tags.reversed {
	color: initial;
	font-weight: normal;
}

.tags-group {
	text-align: left;
	margin: 20px;
}

.tag-item {
	color: #000;
	padding: 2px 4px;
	margin: 0 3px;
	font-size: 12pt;
	background-color: #1890ff;
	opacity: 0.9;
	color: white;
	text-align: center;
	border-radius: 4px;
	display: inline-flex;
	align-items: center;
	justify-content: center;
}

.tag-item.formal {
	background-color: #73d13d;
	border-color: #73d13d;
	color: #fff;
}

.tag-item.uncountable {
	background-color: #faad14;
	border-color: #faad14;
	color: #fff;
}

.tag-item.intransitive {
	background-color: #36cfc9;
	border-color: #36cfc9;
	color: #fff;
}

/* dark-mode */
.nightMode #play-phrase,
.nightMode .extra-example .icon {
	fill: #adadad;
}

.nightMode .tag-item {
	background-color: transparent;
	border: 2px solid gray;
	color: #fff;
}

.nightMode .tag-item.formal {
	background-color: #389e0d;
}

/* mobile device */

.mobile .card {
	font-size: 16pt;
}

#word-pronunciation {
	padding-bottom: 10px;
}
"""
