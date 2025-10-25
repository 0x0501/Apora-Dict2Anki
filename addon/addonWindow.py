import json
import logging
import sys
from copy import deepcopy
from pathlib import Path

from aqt.qt import (
    QAction,
    QKeySequence,
    QDialog,
    QFileDialog,
    QIcon,
    QListWidgetItem,
    Qt,
    QThread,
    pyqtSlot,
)

from .constants import (
    LOG_BUFFER_CAPACITY,
    LOG_FLUSH_INTERVAL,
    MODEL_NAME,
    MODEL_NAME_DISABLED_CONTEXT,
    WINDOW_TITLE,
    BACKWARDS_CARD_TEMPLATE_NAME,
    CARD_SETTINGS,
    RELEASE_URL,
)
from .noteManager import (
    FieldGroup,
    checkModelCardCSS,
    resetModelCardTemplates,
    checkModelFields,
    mergeModelFields,
    checkModelCardTemplates,
    getOrCreateBackwardsCardTemplate,
    deleteBackwardsCardTemplate,
    addNoteToDeck,
    getDeckList,
    getOrCreateDeck,
    getOrCreateModel,
    getWordsByDeck,
    getNoteIDsOfWords,
    getOrCreateNormalCardTemplate,
    loadAssetsIntoCollectionMedia,
)

from . import utils
from .dictionary import DICTIONARIES
from .dictionary.base import (
    CredentialPlatformEnum,
    SimpleWord,
    PronunciationVariantEnum,
)
from .logger import TimedBufferingHandler
from .loginDialog import LoginDialog
from .misc import (
    Mask,
    safe_load_config,
    safe_load_empty_config,
    safe_convert_config_to_dict,
    ConfigType,
    Credential,
)
from .queryApi import QUERY_APIS
from .queryApi.base import QueryAPIPlatformEnum, AbstractQueryAPI, QueryAPIReturnType
from .queryApi.utils import get_pronunciation
from .UIForm import mainUI, wordGroup
from .workers import (
    AssetDownloadWorker,
    LoginStateCheckWorker,
    QueryWorker,
    RemoteWordFetchingWorker,
    VersionCheckWorker,
)
from typing import Callable, Optional

try:
    from aqt import mw
    from aqt.utils import askUser, openLink, showCritical, showInfo, tooltip

except ImportError:
    from test.dummy_aqt import askUser, mw, openLink, showCritical, showInfo, tooltip
    from test.dummy_noteManager import (
        getDeckList,
        getWordsByDeck,
    )

logger = logging.getLogger("dict2Anki")


def fatal_error(exc_type, exc_value, exc_traceback):
    logger.exception(exc_value, exc_info=(exc_type, exc_value, exc_traceback))


# 未知异常日志
sys.excepthook = fatal_error


# change UI slots in `addon/UIForm`
class Windows(QDialog, mainUI.Ui_Dialog):
    isRunning = False

    def __init__(self, parent=None):
        super(Windows, self).__init__(parent)
        self.selectedDict = None
        self.currentConfig = safe_load_empty_config()
        self.localWords: list[str] = []
        self.remoteWordsDict: dict[str, SimpleWord] = {}
        self.selectedGroups: list[list[str]] = [list()] * len(DICTIONARIES)

        self.querySuccessDict: dict[int, QueryAPIReturnType] = {}  # row -> queryResult
        self.queryFailedDict: dict[int, bool] = {}  # row -> bool

        self.added = 0
        self.deleted = 0

        self.workerThread = QThread(self)
        self.workerThread.start()
        self.updateCheckThead = QThread(self)
        self.updateCheckThead.start()
        self.assetDownloadThread = QThread(self)

        self.updateCheckWork = None
        self.loginWorker = None
        self.queryWorker = None
        self.pullWorker = None
        self.assetDownloadWorker = None

        self.setupUi(self)
        self.setWindowTitle(WINDOW_TITLE)
        self.logTextBox.setReadOnly(True)
        self.logTextBox.setUndoRedoEnabled(False)

        # Suppress logs by default, and set default level
        logging.basicConfig(handlers=[logging.NullHandler()], level=logging.INFO)
        # Add custom handler to dict2Anki logger as well as its descendant loggers
        self.logHandler = TimedBufferingHandler(
            self, capacity=LOG_BUFFER_CAPACITY, flush_interval=LOG_FLUSH_INTERVAL
        )
        logger.handlers = [self.logHandler]
        self.setupLogger()

        self.initCore()
        # self.checkUpdate()    # 会导致卡顿
        # self.__dev() # 以备调试时使用

    def closeEvent(self, a0):
        """插件关闭时调用"""
        # cleanup
        for dictionary in DICTIONARIES:
            dictionary.close()
        for api in QUERY_APIS:
            api.close()

        if self.assetDownloadWorker:
            AssetDownloadWorker.close()

        # 退出所有线程
        if self.workerThread.isRunning():
            self.workerThread.requestInterruption()
            self.workerThread.quit()
            self.workerThread.wait()

        if self.updateCheckThead.isRunning():
            self.updateCheckThead.quit()
            self.updateCheckThead.wait()

        if self.assetDownloadThread.isRunning():
            self.assetDownloadThread.requestInterruption()
            self.assetDownloadThread.quit()
            self.assetDownloadThread.wait()

        if a0 is not None:
            a0.accept()

    def on_NewLogRecord(self, text):
        # append to log box, and scroll to bottom
        self.logTextBox.appendPlainText(text)

        vscroll = self.logTextBox.verticalScrollBar()
        if vscroll is not None:
            vscroll.setValue(vscroll.maximum())

    def setupLogger(self):
        """初始化 Logger"""

        def onDestroyed(_self=self):
            logger.removeHandler(_self.logHandler)
            # Safely remove reference to the event emitter without assigning None
            try:
                delattr(_self.logHandler, "eventEmitter")
            except AttributeError:
                pass
            _self.logHandler.close()

        self.logHandler.eventEmitter.newRecord.connect(self.on_NewLogRecord)
        # 日志Widget销毁时移除 Handlers
        self.logTextBox.destroyed.connect(onDestroyed)

    def setupGUIByConfig(self):
        """Setting GUI Widget by reading config file"""
        untypedConfig = mw.addonManager.getConfig(__name__)

        if untypedConfig is None:
            raise Exception("Cannot read config")

        config = safe_load_config(untypedConfig)

        # basic settings
        self.deckComboBox.setCurrentText(config.deck)
        self.dictionaryComboBox.setCurrentIndex(config.selectedDict)
        self.apiComboBox.setCurrentIndex(config.selectedApi)
        if config.selectedGroup:
            self.selectedGroups = config.selectedGroup
        else:
            self.selectedGroups = [list()] * len(DICTIONARIES)

        # account settings
        selectedDictCredential = config.credential[config.selectedDict]
        self.usernameLineEdit.setText(selectedDictCredential.username)
        self.passwordLineEdit.setText(selectedDictCredential.password)
        self.cookieLineEdit.setText(selectedDictCredential.cookie)

        # Apora account settings
        self.AporaAPITokenLineEdit.setText(config.aporaApiToken)

        # sync settings
        self.syncTemplatesCheckbox.setChecked(config.syncTemplates)

        # card settings
        self.termSpeakingRadioButton.setChecked(config.termSpeaking)
        self.contextSpeakingRadioButton.setChecked(config.contextSpeaking)
        self.enableContextCheckBox.setChecked(config.enableContext)
        self.disableSpeakingRadioButton.setChecked(config.disableSpeaking)
        self.GBSpeakingRadioButton.setChecked(config.GreatBritainSpeaking)
        self.USSpeakingRadioButton.setChecked(config.USSpeaking)
        self.enableAddPartOfSpeechToTag.setChecked(config.enableAddPartOfSpeechToTag)
        self.enableChineseCheckBox.setChecked(config.enableChineseDefinition)
        self.enableTermHighlight.setChecked(config.enableTermHighlight)

    def initCore(self):
        # Temporarily disable username/password login, use cookie is more stable
        self.usernameLineEdit.hide()
        self.usernameLabel.hide()
        self.passwordLabel.hide()
        self.passwordLineEdit.hide()

        # load dictionary into combo box
        for d in DICTIONARIES:
            self.dictionaryComboBox.addItem(d.name, d.platform)

        self.apiComboBox.addItems([d.name for d in QUERY_APIS])
        self.deckComboBox.addItems(getDeckList())

        # bind save button and shortcut (Ctrl+S)
        saveSettingsAction = QAction(self)
        saveSettingsAction.setShortcut(QKeySequence.StandardKey.Save)
        saveSettingsAction.triggered.connect(self.getAndSaveCurrentConfig)
        self.addAction(saveSettingsAction)  # add shortcut to current window
        # connect button with action
        self.saveSettingsButton.clicked.connect(self.getAndSaveCurrentConfig)
        self.setupGUIByConfig()
        
        # connect enableTermHighlight and enableContextCheckBox
        self.enableTermHighlight.setEnabled(self.enableContextCheckBox.isChecked())
        self.enableContextCheckBox.toggled.connect(self.on_enable_context_checkbox_change)
        
    def on_enable_context_checkbox_change(self, checked):
        self.enableTermHighlight.setEnabled(checked)

    def getAndSaveCurrentConfig(self) -> ConfigType:
        """获取当前设置，并保存"""
        config, _, _ = self.getAndSaveCurrentConfig_returnMetaInfo()
        return config

    def getAndSaveCurrentConfig_returnMetaInfo(self) -> tuple[ConfigType, bool, bool]:
        """获取当前设置，并返回Meta Info"""
        """:return: (config, configChanged, cardSettingsChanged)"""

        # current config must be identical with project root `config.json`

        print("invoke getAndSaveCurrentConfig_returnMetaInfo()")

        # Get old credential
        untypedOldConfig = mw.addonManager.getConfig(__name__)

        if untypedOldConfig is None:
            raise Exception("Cannot read config file.")

        oldConfig = safe_load_config(untypedOldConfig)

        credential = oldConfig.credential
        # Append the current credential to the old one

        currentSelectedCredentialPlatform: CredentialPlatformEnum = (
            self.dictionaryComboBox.currentData()
        )

        credential[self.dictionaryComboBox.currentIndex()] = Credential(
            platform=currentSelectedCredentialPlatform,
            username=self.usernameLineEdit.text(),
            password=self.passwordLineEdit.text(),
            cookie=self.cookieLineEdit.text(),
        )

        currentConfig = ConfigType(
            # basic settings
            deck=self.deckComboBox.currentText(),
            selectedDict=self.dictionaryComboBox.currentIndex(),
            selectedApi=self.apiComboBox.currentIndex(),
            selectedGroup=self.selectedGroups,
            # account settings
            ##################################
            credential=credential,
            # Apora account settings
            ##################################
            aporaApiToken=self.AporaAPITokenLineEdit.text(),
            # sync settings
            ##################################
            syncTemplates=self.syncTemplatesCheckbox.isChecked(),
            # card settings
            ##################################
            enableChineseDefinition=self.enableChineseCheckBox.isChecked(),
            enableAddPartOfSpeechToTag=self.enableAddPartOfSpeechToTag.isChecked(),
            disableSpeaking=self.disableSpeakingRadioButton.isChecked(),
            GreatBritainSpeaking=self.GBSpeakingRadioButton.isChecked(),
            USSpeaking=self.USSpeakingRadioButton.isChecked(),
            enableContext=self.enableContextCheckBox.isChecked(),
            termSpeaking=self.termSpeakingRadioButton.isChecked(),
            contextSpeaking=self.contextSpeakingRadioButton.isChecked(),
            enableTermHighlight=self.enableTermHighlight.isChecked()
        )

        configChanged, cardSettingsChanged = self._saveConfig(currentConfig)
        self.currentConfig = currentConfig
        return currentConfig, configChanged, cardSettingsChanged

    def _saveConfig(self, config: ConfigType) -> tuple[bool, bool]:
        """:return: (configChanged, cardSettingsChanged)"""
        # get the config currently stored in Anki
        untypedOldConfig = deepcopy(mw.addonManager.getConfig(__name__))

        if untypedOldConfig is None:
            raise Exception("Cannot read oldConfig.")

        # safely convert config into typed ConfigType
        oldConfig = safe_load_config(untypedOldConfig)

        # we compare `ConfigType` by calling __eq__ method that dataclass generated
        configChanged = config == oldConfig

        if configChanged:
            logger.info("Config has no changes.")
            return False, False

        cardSettingsChanged = False

        for setting in CARD_SETTINGS:
            if getattr(config, setting) != getattr(oldConfig, setting):
                cardSettingsChanged = True

        logger.info(
            f"configChanged: {configChanged}, cardSettingsChanged: {cardSettingsChanged}"
        )
        logger.info(f"Saving config: {self._mask_config(config)}")
        mw.addonManager.writeConfig(__name__, safe_convert_config_to_dict(config))
        return configChanged, cardSettingsChanged

    def _mask_config(self, config: ConfigType) -> object:
        """Mostly for logging purposes, mask secrets with `***********`"""
        maskedConfig = deepcopy(config)

        # Only mask the nonempty fields
        maskedCredential = [
            Credential(
                platform=c.platform,
                username=c.username,
                password=repr(Mask(c.password)) if len(c.password) > 0 else "",
                cookie=repr(Mask(c.cookie)) if len(c.cookie) > 0 else "",
            )
            for c in maskedConfig.credential
        ]
        maskedConfig.credential = maskedCredential
        return maskedConfig

    def getFieldGroup(self, config: ConfigType) -> FieldGroup:
        """Check current card settings and toggle off corresponding fields"""
        fg = FieldGroup()
        for field in CARD_SETTINGS:
            if not hasattr(config, field):
                logger.info(
                    f"FieldGroup: '{field}' is toggled off. Will remove it from templates."
                )
                fg.toggleOff(field)
        return fg

    # TODO: check new version
    def checkUpdate(self):
        @pyqtSlot(str, str)
        def on_haveNewVersion(version, changeLog):
            if askUser(f"有新版本:{version}是否更新？\n\n{changeLog.strip()}"):
                openLink(RELEASE_URL)

        self.updateCheckWork = VersionCheckWorker()
        self.updateCheckWork.moveToThread(self.updateCheckThead)
        self.updateCheckWork.haveNewVersion.connect(on_haveNewVersion)
        self.updateCheckWork.finished.connect(self.updateCheckThead.quit)
        self.updateCheckWork.start.connect(self.updateCheckWork.run)
        self.updateCheckWork.start.emit()

    @pyqtSlot(int)
    def on_dictionaryComboBox_currentIndexChanged(self, index):
        """词典候选框改变事件"""
        self.currentDictionaryLabel.setText(
            f"当前选择词典: {self.dictionaryComboBox.currentText()}"
        )
        untypedConfig = mw.addonManager.getConfig(__name__)

        if untypedConfig is None:
            raise Exception("Cannot read config.")

        config = safe_load_config(untypedConfig)

        # self.cookieLineEdit.setText(config["credential"][index]["cookie"])

        # if no credential stored in the config.json
        if len(config.credential) == 0:
            self.cookieLineEdit.setText("")
        else:
            self.cookieLineEdit.setText(config.credential[index].cookie)

    @pyqtSlot()
    def on_btnImportFromFiles_clicked(self):
        """Button: Import words from txt files"""
        if not self.deckComboBox.currentText():
            showInfo("\n请选择或输入要同步的牌组")
            return

        # if word boxes are not empty, warn user before proceeding
        if (
            self.newWordListWidget.count() > 0
            or self.needDeleteWordListWidget.count() > 0
        ):
            if not askUser(
                "The words boxes are not empty! Clear the words and continue?",
                defaultno=True,
            ):
                logger.info("Aborted")
                self.logHandler.flush()
                return
        # clear the word boxes
        self.newWordListWidget.clear()
        self.needDeleteWordListWidget.clear()

        # choose txt files
        homedir = str(Path.home())
        filenames, _ = QFileDialog.getOpenFileNames(
            self, "Select Files", homedir, "Text Files (*.txt)"
        )
        if not filenames:
            logger.info("No files selected.")
            self.logHandler.flush()
            return

        logger.info(f"filenames: {filenames}")
        self.logHandler.flush()

        words: list[SimpleWord] = []
        for filename in filenames:
            logger.info(f"Reading words from {filename}...")
            words_in_file = [
                SimpleWord.from_values(values_in_line)
                for values_in_line in utils.read_words_from_file(filename)
            ]
            # Filter out None values returned by SimpleWord.from_values before extending
            words_in_file = [w for w in words_in_file if w is not None]
            logger.info(
                f"[OK] Found {len(words_in_file)} words (may including duplicates)."
            )
            words.extend(words_in_file)
        logger.info("------------------------------")
        logger.info(
            f"Total: Found {len(words)} words (may including duplicates) in {len(filenames)} files."
        )
        self.logHandler.flush()
        if not askUser(
            f"Found {len(words)} words (may including duplicates) in {len(filenames)} files. Import now?"
        ):
            logger.info("Aborted")
            self.logHandler.flush()
            return

        logger.info("Start importing")
        self.localWords = getWordsByDeck(self.deckComboBox.currentText())
        self.remoteWordsDict = {}
        self.insertWordToListWidget(words)
        self.on_allPullWork_done()

    @pyqtSlot()
    def on_pullRemoteWordsBtn_clicked(self):
        """获取单词按钮点击事件"""
        if not self.deckComboBox.currentText():
            showInfo("\n请选择或输入要同步的牌组")
            return

        self.mainTab.setEnabled(False)
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(0)

        currentConfig = self.getAndSaveCurrentConfig()
        self.selectedDict = DICTIONARIES[currentConfig.selectedDict]()

        # 登陆线程
        self.loginWorker = LoginStateCheckWorker(
            self.selectedDict.checkCookie,
            json.loads(self.cookieLineEdit.text() or "{}"),
        )
        self.loginWorker.moveToThread(self.workerThread)
        self.loginWorker.start.connect(self.loginWorker.run)
        self.loginWorker.logSuccess.connect(self.onLogSuccess)
        self.loginWorker.logFailed.connect(self.onLoginFailed)
        self.loginWorker.start.emit()

    @pyqtSlot()
    def onLoginFailed(self):
        showCritical("第一次登录或cookie失效!请重新登录")
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(1)
        self.mainTab.setEnabled(True)
        self.cookieLineEdit.clear()
        # Ensure selectedDict is initialized before accessing its attributes
        if self.selectedDict is None:
            idx = self.dictionaryComboBox.currentIndex()
            self.selectedDict = DICTIONARIES[idx]()
        self.loginDialog = LoginDialog(
            loginUrl=self.selectedDict.loginUrl,
            loginCheckCallbackFn=self.selectedDict.loginCheckCallbackFn,
            parent=self,
        )
        self.loginDialog.loginSucceed.connect(self.onLogSuccess)
        self.loginDialog.show()

    @pyqtSlot(str)
    def onLogSuccess(self, cookie: str) -> None:
        self.cookieLineEdit.setText(cookie)
        self.getAndSaveCurrentConfig()

        # TODO: is it really save?

        # Ensure selectedDict is initialized before using it
        if self.selectedDict is None:
            # try to get the selected dict index from currentConfig, fallback to combobox
            try:
                selected_idx = getattr(
                    self.currentConfig,
                    "selectedDict",
                    self.dictionaryComboBox.currentIndex(),
                )
            except Exception:
                selected_idx = self.dictionaryComboBox.currentIndex()
            self.selectedDict = DICTIONARIES[selected_idx]()
        self.selectedDict.checkCookie(json.loads(cookie))
        groups = self.selectedDict.getGroups()
        if groups:
            logger.info(f"{len(groups)} group(s): {groups}")
        else:
            logger.warning("group is None!")

        def onAccepted(is_popup=True):
            """选择单词本弹窗确定事件"""
            # 清空 listWidget
            self.newWordListWidget.clear()
            self.needDeleteWordListWidget.clear()
            self.mainTab.setEnabled(False)

            if not is_popup:
                selectedGroups = self.selectedGroups[self.currentConfig.selectedDict]
            else:
                selectedGroups = []
                for index in range(group.wordGroupListWidget.count()):
                    item = group.wordGroupListWidget.item(index)
                    if item is not None and item.checkState() == Qt.CheckState.Checked:
                        selectedGroups.append(item.text())
            # 保存分组记录
            self.selectedGroups[self.currentConfig.selectedDict] = selectedGroups
            self.progressBar.setValue(0)
            self.progressBar.setMaximum(1)
            logger.info(f"选中单词本{selectedGroups}")
            self.getRemoteWordList(selectedGroups)

        def onRejected():
            """选择单词本弹窗取消事件"""
            self.progressBar.setValue(0)
            self.progressBar.setMaximum(1)
            self.mainTab.setEnabled(True)

        # Avoid popup when there's only 1 group
        if len(groups) == 1:
            logger.info("Only 1 group. Select automatically and avoid popup.")
            group_name, group_index = groups[0]
            selectedDict = self.currentConfig.selectedDict
            if not self.selectedGroups[selectedDict]:
                self.selectedGroups[selectedDict] = list()
            self.selectedGroups[selectedDict] = [group_name]
            onAccepted(is_popup=False)
            return

        # Otherwise, popup a dialog
        container = QDialog(self)
        group = wordGroup.Ui_Dialog()
        group.setupUi(container)
        for groupName in [
            str(group_name) for group_name, _ in self.selectedDict.groups
        ]:
            item = QListWidgetItem()
            item.setFlags(
                Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsEnabled
            )
            item.setText(groupName)
            item.setCheckState(Qt.CheckState.Unchecked)
            group.wordGroupListWidget.addItem(item)
        # 恢复上次选择的单词本分组
        selectedDict = self.currentConfig.selectedDict
        if not self.selectedGroups[selectedDict]:
            self.selectedGroups[selectedDict] = list()
        for groupName in self.selectedGroups[selectedDict]:
            items = group.wordGroupListWidget.findItems(
                groupName, Qt.MatchFlag.MatchExactly
            )
            for item in items:
                item.setCheckState(Qt.CheckState.Checked)
        group.buttonBox.accepted.connect(onAccepted)
        group.buttonBox.rejected.connect(onRejected)
        container.exec()

    def getRemoteWordList(self, selected_groups: list[str]):
        """根据选中到分组获取分组下到全部单词，并添加到 newWordListWidget"""
        # Ensure selectedDict is initialized to avoid accessing attributes on None
        if self.selectedDict is None:
            try:
                idx = self.dictionaryComboBox.currentIndex()
                self.selectedDict = DICTIONARIES[idx]()
            except Exception as e:
                logger.error(f"Failed to initialize selectedDict: {e}")
                showCritical("未能初始化词典实例，无法获取远程单词列表。")
                return

        group_map = dict(self.selectedDict.groups)
        self.localWords = getWordsByDeck(self.deckComboBox.currentText())
        self.remoteWordsDict = {}

        # 启动单词获取线程
        self.pullWorker = RemoteWordFetchingWorker(
            self.selectedDict,
            [
                (
                    group_name,
                    group_map[group_name],
                )
                for group_name in selected_groups
            ],
        )
        self.pullWorker.moveToThread(self.workerThread)
        self.pullWorker.start.connect(self.pullWorker.run)
        self.pullWorker.tick.connect(
            lambda: self.progressBar.setValue(self.progressBar.value() + 1)
        )
        self.pullWorker.setProgress.connect(self.progressBar.setMaximum)
        self.pullWorker.doneThisGroup.connect(self.insertWordToListWidget)
        self.pullWorker.done.connect(self.on_allPullWork_done)
        self.pullWorker.start.emit()

    @pyqtSlot(list)
    def insertWordToListWidget(self, words: list[SimpleWord]):
        """一个分组获取完毕事件"""
        for word in words:
            self.remoteWordsDict[word.term] = word
            wordItem = QListWidgetItem(word.term, self.newWordListWidget)
            wordItem.setData(Qt.ItemDataRole.UserRole, None)
        self.newWordListWidget.clearSelection()

    @pyqtSlot()
    def on_allPullWork_done(self):
        """全部分组获取完毕事件"""
        # termList: [str]
        localTermList: set[str] = set(getWordsByDeck(self.deckComboBox.currentText()))
        remoteTermList: set[str] = set()
        for row in range(self.newWordListWidget.count()):
            item = self.newWordListWidget.item(row)
            if item is not None:
                remoteTermList.add(item.text())

        newTerms: set[str] = utils.set_sub_ignore_case(
            remoteTermList, localTermList
        )  # 新单词
        needToDeleteTerms: set[str] = utils.set_sub_ignore_case(
            localTermList, remoteTermList
        )  # 需要删除的单词
        logger.info(f"本地({len(localTermList)}): {localTermList}")
        logger.info(f"远程({len(remoteTermList)}): {remoteTermList}")
        logger.info(f"待查({len(newTerms)}): {newTerms}")
        logger.info(f"待删({len(needToDeleteTerms)}): {needToDeleteTerms}")
        waitIcon = QIcon(":/icons/wait.png")
        delIcon = QIcon(":/icons/delete.png")
        self.newWordListWidget.clear()
        self.needDeleteWordListWidget.clear()

        for term in needToDeleteTerms:
            item = QListWidgetItem(term)
            # item.setCheckState(Qt.CheckState.Checked)
            item.setCheckState(
                Qt.CheckState.Unchecked
            )  # Defaults to Unchecked (Avoid unintentional data loss)
            item.setIcon(delIcon)
            self.needDeleteWordListWidget.addItem(item)

        for term in newTerms:
            item = QListWidgetItem(term)
            item.setIcon(waitIcon)
            self.newWordListWidget.addItem(item)
        self.newWordListWidget.clearSelection()

        self.dictionaryComboBox.setEnabled(True)
        self.apiComboBox.setEnabled(True)
        self.deckComboBox.setEnabled(True)
        self.pullRemoteWordsBtn.setEnabled(True)
        self.queryBtn.setEnabled(self.newWordListWidget.count() > 0)
        self.btnSync.setEnabled(
            self.newWordListWidget.count() == 0
            and self.needDeleteWordListWidget.count() > 0
        )
        if self.needDeleteWordListWidget.count() == self.newWordListWidget.count() == 0:
            logger.info("无需同步")
            tooltip("无需同步")
        self.mainTab.setEnabled(True)
        self.logHandler.flush()

    @pyqtSlot()
    def on_queryBtn_clicked(self):
        logger.info("点击查询按钮")
        self.querySuccessDict = {}
        self.queryFailedDict = {}
        currentConfig = self.getAndSaveCurrentConfig()
        self.queryBtn.setEnabled(False)
        self.pullRemoteWordsBtn.setEnabled(False)
        self.btnSync.setEnabled(False)

        # if the query api is Apora, make sure API token is set before querying terms
        selectedQueryAPI = QUERY_APIS[currentConfig.selectedApi]

        if (
            selectedQueryAPI.platform == QueryAPIPlatformEnum.APORA
            and len(currentConfig.aporaApiToken) == 0
        ):
            showInfo("必须填写Apora API Token")
            self.queryBtn.setEnabled(True)
            self.pullRemoteWordsBtn.setEnabled(True)
            self.btnSync.setEnabled(True)
            return

        wordList: list[tuple[SimpleWord, int]] = []  # [(SimpleWord, row)]
        selectedTerms = self.newWordListWidget.selectedItems()
        if selectedTerms:
            # 如果选中单词则只查询选中的单词
            for termItem in selectedTerms:
                if termItem is None:
                    continue
                row = self.newWordListWidget.row(termItem)
                term_text = termItem.text()
                if term_text not in self.remoteWordsDict:
                    logger.warning(
                        f"Selected term '{term_text}' not found in remoteWordsDict; skipping"
                    )
                    continue
                word = self.remoteWordsDict[term_text]
                wordList.append((word, row))
        else:  # 没有选择则查询全部
            for row in range(self.newWordListWidget.count()):
                termItem = self.newWordListWidget.item(row)
                if termItem is None:
                    continue
                term_text = termItem.text()
                if term_text not in self.remoteWordsDict:
                    logger.warning(
                        f"Term '{term_text}' at row {row} not found in remoteWordsDict; skipping"
                    )
                    continue
                word = self.remoteWordsDict[term_text]
                wordList.append((word, row))

        logger.info(f"待查询单词{wordList}")
        # 查询线程
        self.progressBar.setMaximum(len(wordList))
        self.queryWorker = QueryWorker(wordList, QUERY_APIS[currentConfig.selectedApi])
        self.queryWorker.moveToThread(self.workerThread)
        self.queryWorker.thisRowDone.connect(self.on_thisRowDone)
        self.queryWorker.thisRowFailed.connect(self.on_thisRowFailed)
        self.queryWorker.tick.connect(
            lambda: self.progressBar.setValue(self.progressBar.value() + 1)
        )
        self.queryWorker.allQueryDone.connect(self.on_allQueryDone)
        self.queryWorker.start.connect(self.queryWorker.run)
        self.queryWorker.start.emit()

    @pyqtSlot(int, QueryAPIReturnType)
    def on_thisRowDone(self, row, result: QueryAPIReturnType):
        """该行单词查询完毕"""
        self.querySuccessDict[row] = result

    @pyqtSlot(int)
    def on_thisRowFailed(self, row):
        self.queryFailedDict[row] = True

    doneIcon = QIcon(":/icons/done.png")
    failedIcon = QIcon(":/icons/failed.png")

    @pyqtSlot()
    def on_allQueryDone(self):
        # update icons
        failed = []
        for row in range(self.newWordListWidget.count()):
            wordItem = self.newWordListWidget.item(row)

            if wordItem is None:
                raise Exception("Cannot get wordItem.")

            if row in self.querySuccessDict:
                wordItem.setIcon(self.doneIcon)
                wordItem.setData(Qt.ItemDataRole.UserRole, self.querySuccessDict[row])
            elif row in self.queryFailedDict:
                wordItem.setIcon(self.failedIcon)
                failed.append(wordItem.text())

        if failed:
            logger.warning(f"查询失败或未查询:{failed}")

        self.pullRemoteWordsBtn.setEnabled(True)
        self.queryBtn.setEnabled(True)
        self.btnSync.setEnabled(True)
        self.logHandler.flush()

    def get_preferred_pronunciation_variant(
        self, currentConfig: Optional[ConfigType]
    ) -> PronunciationVariantEnum:
        if currentConfig is not None and currentConfig.disableSpeaking:
            return PronunciationVariantEnum.NONE  # No speaking
        else:
            return (
                PronunciationVariantEnum.US
                if self.USSpeakingRadioButton.isChecked()
                else PronunciationVariantEnum.UK
            )

    def get_asset_download_task(
        self, word: QueryAPIReturnType, preferred_pron: PronunciationVariantEnum
    ):
        image_task = None
        term = word.term
        # if word["image"]:
        #     imageFilename = default_image_filename(term)
        #     image_task = (imageFilename, word["image"])
        # else:
        # logger.info(f"No image for word {term}")
        
        if word.context_audio_url is None or word.term_audio_url is None:
            logger.warning(f"No audio download link was founded for word {term}!")
            return image_task, None, PronunciationVariantEnum.NONE, False

        pron_type, is_fallback = get_pronunciation(word, preferred_pron)
        if pron_type == PronunciationVariantEnum.NONE:
            if is_fallback:
                logger.warning(f"No audio for word {term}!")
            return image_task, None, PronunciationVariantEnum.NONE, False

        if is_fallback:
            logger.warning(
                f"Pronunciation: {preferred_pron.name} is missing for word {term}. Downloading {pron_type.name} instead."
            )

        pronFilename = utils.default_audio_filename(term=term, format="wav")
        logger.info(f"Audio file for: ${term}: ${pronFilename}")
        if word.context_audio_url:
            audio_task = (pronFilename, word.context_audio_url) # (filename, download file url)
        elif word.term_audio_url:
            audio_task = (pronFilename, word.term_audio_url)
        else:
            audio_task = None
        return image_task, audio_task, pron_type, is_fallback

    @pyqtSlot()
    def on_btnSync_clicked(self):
        logger.info("Sync button clicked")
        logger.info("Check query results")
        self.logHandler.flush()
        failedGenerator = (
            (item := self.newWordListWidget.item(row)) is None
            or item.data(Qt.ItemDataRole.UserRole) is None
            for row in range(self.newWordListWidget.count())
        )
        if any(failedGenerator):
            if not askUser(
                '存在未查询或失败的单词，确定要加入单词本吗？\n 你可以选择失败的单词点击 "查询按钮" 来重试。'
            ):
                return

        logger.info("Get and save current config")
        self.logHandler.flush()
        # currentConfig = self.getAndSaveCurrentConfig()
        currentConfig, configChanged, cardSettingsChanged = (
            self.getAndSaveCurrentConfig_returnMetaInfo()
        )
        fg = self.getFieldGroup(currentConfig)

        # create Note Type/Model
        logger.info("Create Note Type/Model")
        self.logHandler.flush()
        newCreated, fieldsUpdated = True, True
        try:
            if currentConfig.enableContext:
                model, newCreated, fieldsUpdated = getOrCreateModel(MODEL_NAME)
            else:
                model, newCreated, fieldsUpdated = getOrCreateModel(MODEL_NAME_DISABLED_CONTEXT, disableContext=True)
        except Exception as err:
            logger.warning(err)
            if not askUser(
                f"{err}\nDeleting it would delete ALL its cards and notes!!! Continue?",
                defaultno=True,
            ):
                logger.info("Aborted")
                self.logHandler.flush()
                return
            if not askUser(
                f"[DANGEROUS ACTION!!!] Are you sure to delete model '{MODEL_NAME}' AND all its cards/notes???",
                defaultno=True,
            ):
                logger.info("Aborted upon second reminder")
                self.logHandler.flush()
                return
            # force delete the existing model
            if currentConfig.enableContext:
                (model, _, _) = getOrCreateModel(modelName=MODEL_NAME, recreate=True)  # type: ignore
            else:
                (model, _, _) = getOrCreateModel(modelName=MODEL_NAME_DISABLED_CONTEXT, recreate=True)

        if newCreated:
            # create 'Normal' card template (card type)
            logger.info("Create card templates for the new created model.")
            self.logHandler.flush()
            getOrCreateNormalCardTemplate(model, fg)
            # create 'Backwards' card template (card type)
            # getOrCreateBackwardsCardTemplate(model)

            # we need to ensure the fonts and js file are loaded into `collection.media`
            loadAssetsIntoCollectionMedia()

        else:
            logger.info("Found existing model.")
            if currentConfig.syncTemplates:
                logger.info(
                    "Reset card templates to default (FieldGroup settings will be respected)."
                )
                self.logHandler.flush()
                resetModelCardTemplates(model, fg)
            else:
                logger.info("Skip Templates Sync as it has been turned off.")

        # else:           # existing model. (Let's make it simple: Reset card templates to default upon every sync.)
        #     logger.info(f"Found existing model. Reset card templates to default (FieldGroup settings will be respected).")
        #     self.logHandler.flush()
        #     resetModelCardTemplates(model, fg)
        # elif fieldsUpdated:     # existing model, but fields have been updated/merged
        #     resetModelCardTemplates(model, fg)
        # else:                   # existing model, and fields have not been updated/merged
        #     pass

        # create deck
        deck = getOrCreateDeck(self.deckComboBox.currentText(), model=model)

        imagesDownloadTasks = []
        audiosDownloadTasks : list[tuple[str, str]]= []
        newWordCount = self.newWordListWidget.count()

        # 判断是否需要下载发音
        preferred_pron = self.get_preferred_pronunciation_variant(currentConfig)
        if preferred_pron == PronunciationVariantEnum.NONE:
            logger.info("不下载发音")
        else:
            logger.info(
                f"Preferred Pronunciation: {preferred_pron.name}"
            )  # print enum name

        self.added = 0
        for row in range(newWordCount):
            wordItem = self.newWordListWidget.item(row)

            if wordItem is None:
                raise Exception("Cannot get wordItem")

            wordItemData: QueryAPIReturnType = wordItem.data(Qt.ItemDataRole.UserRole)
            # print("WordItemData")
            # print(wordItemData)
            if wordItemData:
                term = wordItemData.term
                logger.debug(f"wordItemData ({term}): {wordItemData}")
                # Add asset download task (image and audio)
                image_task, audio_task, pron_type, is_fallback = (
                    self.get_asset_download_task(wordItemData, preferred_pron)
                )
                if image_task:
                    imagesDownloadTasks.append(image_task)
                if audio_task:
                    logger.info(f"添加Audio Task: {audio_task}")
                    audiosDownloadTasks.append(audio_task)

                # add note
                addNoteToDeck(
                    deck=deck,
                    model=model,
                    config=currentConfig,
                    word=wordItemData,
                    pronunciationVariant=pron_type,
                    existing_note=None,
                    overwrite=False,
                )
                self.added += 1
        mw.reset()

        # download assets
        if len(imagesDownloadTasks) > 0 or len(audiosDownloadTasks) > 0:
            self.btnSync.setEnabled(False)
            self.downloadAssets(
                imagesDownloadTasks, audiosDownloadTasks, self.on_assetsDownloadDone
            )

        self.newWordListWidget.clear()

        needToDeleteWordItems = []
        for row in range(self.needDeleteWordListWidget.count()):
            item = self.needDeleteWordListWidget.item(row)
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                needToDeleteWordItems.append(item)
        needToDeleteWords = [i.text() for i in needToDeleteWordItems]

        self.deleted = 0

        if needToDeleteWords and askUser(
            f"确定要删除这些单词吗:{needToDeleteWords[:3]}...({len(needToDeleteWords)}个)",
            title="Apora Dict2Anki",
            parent=self,
        ):
            logger.info(f"需要删除({len(needToDeleteWords)}) - {needToDeleteWords}")
            needToDeleteWordNoteIds = getNoteIDsOfWords(
                needToDeleteWords, currentConfig.deck
            )

            if mw.col is None:
                raise Exception("mw.col is none")

            mw.col.remNotes(needToDeleteWordNoteIds)
            self.deleted += len(needToDeleteWordNoteIds)
            mw.col.reset()
            mw.reset()
            for item in needToDeleteWordItems:
                self.needDeleteWordListWidget.takeItem(
                    self.needDeleteWordListWidget.row(item)
                )
            logger.info(f"实际删除({self.deleted})")
        logger.info("完成")

        if not (imagesDownloadTasks or audiosDownloadTasks):
            self.printSyncReport()
        self.logHandler.flush()

    def printSyncReport(self):
        logger.info(f"Added: {self.added}, Deleted: {self.deleted}")

    def downloadAssets(self, imagesDownloadTasks, audiosDownloadTasks: list[tuple[str, str]], done_func: Callable):
        logger.info(
            f"Image download tasks({len(imagesDownloadTasks)}): {imagesDownloadTasks}"
        )
        logger.info(
            f"Audio download tasks({len(audiosDownloadTasks)}): {audiosDownloadTasks}"
        )
        if imagesDownloadTasks or audiosDownloadTasks:
            self.progressBar.setValue(0)
            self.progressBar.setMaximum(
                len(imagesDownloadTasks) + len(audiosDownloadTasks)
            )
            if self.assetDownloadThread is not None:
                self.assetDownloadThread.requestInterruption()
                self.assetDownloadThread.quit()
                self.assetDownloadThread.wait()

            self.assetDownloadThread = QThread(self)
            self.assetDownloadThread.start()

            if mw.col is None:
                raise Exception("mw.col is none")

            self.assetDownloadWorker = AssetDownloadWorker(
                mw.col.media.dir(), imagesDownloadTasks, audiosDownloadTasks
            )
            self.assetDownloadWorker.moveToThread(self.assetDownloadThread)
            self.assetDownloadWorker.tick.connect(
                lambda: self.progressBar.setValue(self.progressBar.value() + 1)
            )
            self.assetDownloadWorker.start.connect(self.assetDownloadWorker.run)
            self.assetDownloadWorker.done.connect(done_func)
            self.assetDownloadWorker.start.emit()

    # =================================== Utilities =================================== #
    @pyqtSlot()
    def on_assetsDownloadDone(self):
        self.assetDownloadThread.quit()
        tooltip("图片音频下载完成")
        logger.info("图片音频下载完成")
        self.printSyncReport()
        self.logHandler.flush()

    def queryWords(
        self,
        wordList: list[tuple[SimpleWord, int]],
        dictAPI: type[AbstractQueryAPI],
        all_done_func: Callable[[], None],
    ):
        # self.progressBar.setMaximum(len(wordList))
        self.queryWorker = QueryWorker(wordList, dictAPI)
        self.queryWorker.moveToThread(self.workerThread)
        self.queryWorker.thisRowDone.connect(self.on_thisRowDone)
        self.queryWorker.thisRowFailed.connect(self.on_thisRowFailed)
        # self.queryWorker.tick.connect(lambda: self.progressBar.setValue(self.progressBar.value() + 1))
        self.queryWorker.allQueryDone.connect(all_done_func)
        self.queryWorker.start.connect(self.queryWorker.run)
        self.queryWorker.start.emit()

    tmp_currentConfig = None
    """for DownloadMissingAssets or FillMissingValues only"""

    @pyqtSlot()
    def on_btnDownloadMissingAssets_clicked(self):
        """Download missing assets for all notes of type Dict2Anki in ALL decks"""
        self.tmp_currentConfig = self.getAndSaveCurrentConfig()

        if mw.col is None:
            raise Exception("mw.col is none")

        noteIds = mw.col.find_notes(f"note:{MODEL_NAME}")
        logger.info(f"Found ({len(noteIds)}) notes of type '{MODEL_NAME}'")
        self.logHandler.flush()

        # find words that have missing assets
        wordList: list[tuple[SimpleWord, int]] = []  # [(SimpleWord, row)]
        for noteId in noteIds:
            note = mw.col.get_note(noteId)
            term = note["term"]
            media_dir = mw.col.media.dir()
            # logger.info(f"Checking term {term}")
            if utils.is_image_file_missing(
                note["image"], media_dir
            ) or utils.is_audio_file_missing(note["pronunciation"], media_dir):
                # logger.warning(f"image or audio file is missing for [{term}]")
                word, row = SimpleWord(term), len(wordList)
                wordList.append((word, row))
        terms = [w.term for w, r in wordList]
        if not terms:
            logger.info("[All clear] Nothing to do.")
            self.logHandler.flush()
            tooltip("Nothing to do.")
            return

        logger.info(f"{len(terms)} words have missing assets: {terms}")
        self.logHandler.flush()
        if not askUser(f"{len(terms)} words have missing assets. Download now?"):
            logger.info("Aborted")
            self.logHandler.flush()
            return

        # query words
        self.querySuccessDict = {}
        self.queryFailedDict = {}
        self.queryWords(
            wordList,
            QUERY_APIS[self.tmp_currentConfig.selectedApi],
            self.__on_allQueryDone_DownloadMissingAssets,
        )

    @pyqtSlot()
    def __on_allQueryDone_DownloadMissingAssets(self):
        """for btnDownloadMissingAssets"""
        logger.info(
            f"[Query complete] Success: {len(self.querySuccessDict)}, Failed: {len(self.queryFailedDict)}"
        )
        if self.queryFailedDict:
            logger.warning(f"{len(self.queryFailedDict)} words query failed.")
            if not askUser(
                f"{len(self.queryFailedDict)} words query failed. Continue anyway?"
            ):
                logger.info("Aborted")
                return
        # download missing assets
        logger.info("------------------------------------------")
        logger.info("Iterate over query results: download missing assets")
        self.logHandler.flush()

        preferred_pron = self.get_preferred_pronunciation_variant(
            self.tmp_currentConfig
        )
        if preferred_pron == PronunciationVariantEnum.NONE:
            logger.info("不下载发音")
        else:
            logger.info(f"Preferred Pronunciation: {preferred_pron.name}")

        imagesDownloadTasks = []
        audiosDownloadTasks = []
        for row, word in self.querySuccessDict.items():
            term = word.term
            logger.debug(f"word ({term}): {word}")
            # Add asset download task (image and audio)
            image_task, audio_task, pron_type, is_fallback = (
                self.get_asset_download_task(word, preferred_pron)
            )
            if image_task:
                imagesDownloadTasks.append(image_task)
            if audio_task:
                audiosDownloadTasks.append(audio_task)
        # download assets
        self.downloadAssets(
            imagesDownloadTasks,
            audiosDownloadTasks,
            self.__on_assetsDownloadDone_DownloadMissingAssets,
        )

    @pyqtSlot()
    def __on_assetsDownloadDone_DownloadMissingAssets(self):
        """for btnDownloadMissingAssets"""
        self.assetDownloadThread.quit()
        logger.info("Download complete!")
        self.logHandler.flush()

    tmp_noteDict: dict = {}  # term -> Note
    """for FillMissingValues only"""

    @pyqtSlot()
    def on_btnFillMissingValues_clicked(self):
        """Fill missing field values for all notes of type Dict2Anki in ALL decks.
        This function may take some time."""
        self.tmp_noteDict = {}
        self.tmp_currentConfig = self.getAndSaveCurrentConfig()
        if mw.col is None:
            raise Exception("mw.col is none")
        noteIds = mw.col.find_notes(f"note:{MODEL_NAME}")
        logger.info(f"Found ({len(noteIds)}) notes of type '{MODEL_NAME}'")
        self.logHandler.flush()

        if not askUser(
            f"This operation will take some time to fill missing field values for notes of type '{MODEL_NAME}' ({len(noteIds)}). Continue?",
            defaultno=True,
        ):
            logger.info("Aborted")
            self.logHandler.flush()
            return

        # load all notes, and generate word list, as well as note dict
        wordList: list[tuple[SimpleWord, int]] = []  # [(SimpleWord, row)]
        for noteId in noteIds:
            note = mw.col.get_note(noteId)
            term = note["term"]
            self.tmp_noteDict[term] = note
            word, row = SimpleWord(term), len(wordList)
            wordList.append((word, row))

        if not wordList:
            logger.info("No words.")
            self.logHandler.flush()
            tooltip("No words.")
            return

        # query words
        self.querySuccessDict = {}
        self.queryFailedDict = {}
        self.queryWords(
            wordList,
            QUERY_APIS[self.tmp_currentConfig.selectedApi],
            self.__on_allQueryDone_FillMissingValues,
        )

    @pyqtSlot()
    def __on_allQueryDone_FillMissingValues(self):
        """for btnFillMissingValues"""
        logger.info(
            f"[Query complete] Success: {len(self.querySuccessDict)}, Failed: {len(self.queryFailedDict)}"
        )
        self.logHandler.flush()
        if self.queryFailedDict:
            logger.warning(f"{len(self.queryFailedDict)} words query failed.")
            if not askUser(
                f"{len(self.queryFailedDict)} words query failed. Continue anyway?"
            ):
                logger.info("Aborted")
                self.logHandler.flush()
                return
        # update notes (fill missing field values)
        logger.info("------------------------------------------")
        logger.info(
            "Iterate over query results: update notes (fill missing field values)"
        )
        self.logHandler.flush()
        preferred_pron = self.get_preferred_pronunciation_variant(
            self.tmp_currentConfig
        )
        if preferred_pron == PronunciationVariantEnum.NONE:
            logger.info("不下载发音")
        else:
            logger.info(f"Preferred Pronunciation: {preferred_pron}")

        self.logHandler.flush()
        for row, word in self.querySuccessDict.items():
            term = word.term
            logger.debug(f"word ({term}): {word}")
            # resolve image and audio information (for use in field values)
            image_task, audio_task, pron_type, is_fallback = (
                self.get_asset_download_task(word, preferred_pron)
            )
            # update note (fill missing field values)
            existing_note = self.tmp_noteDict[term]
            # Ensure tmp_currentConfig is not None before passing to addNoteToDeck
            if self.tmp_currentConfig is None:
                raise Exception("tmp_currentConfig is None")

            # Downloading missing assets don't need model and deck
            addNoteToDeck(
                deck=None,
                model=None,
                config=self.tmp_currentConfig,
                word=word,
                pronunciationVariant=pron_type,
                existing_note=existing_note,
                overwrite=False,
            )
        mw.reset()
        self.logHandler.flush()
        logger.info("Done!")
        self.logHandler.flush()

    @pyqtSlot()
    def on_btnExportAudio_clicked(self):
        tooltip("btnExportAudio Clicked!")

    @pyqtSlot()
    def on_btnBackwardTemplate_clicked(self):
        """Add Or Delete Backwards Card Template (Card Type)"""

        if mw.col is None:
            raise Exception("mw.col is none")

        modelObject = mw.col.models.by_name(MODEL_NAME)
        if not modelObject:
            showInfo(
                f"Model (Note Type) '{MODEL_NAME}' does not exist! Please Sync first!"
            )
            return

        backwardsTemplate = None
        for temp in modelObject["tmpls"]:
            if temp["name"] == BACKWARDS_CARD_TEMPLATE_NAME:
                backwardsTemplate = temp
                break

        if backwardsTemplate:
            if askUser("Are you sure to DELETE Backwards template?", defaultno=True):
                try:
                    deleteBackwardsCardTemplate(modelObject, backwardsTemplate)
                    logger.info("Deleted Backwards template")
                    tooltip("Deleted")
                except AssertionError as err:
                    logger.error(f"Failed to delete Backwards template: {err}")
                    tooltip("Failed!")
        else:
            if askUser("Add Backwards template now?", defaultno=True):
                try:
                    currentConfig = self.getAndSaveCurrentConfig()
                    fg = self.getFieldGroup(currentConfig)
                    getOrCreateBackwardsCardTemplate(modelObject, fg)
                    logger.info("Added Backward template")
                    tooltip("Added")
                except Exception as e:
                    logger.error(e)
                    tooltip("Failed!")
        self.logHandler.flush()

    @pyqtSlot()
    def on_btnCheckTemplates_clicked(self):
        logger.info(f"Checking Card Templates for model {MODEL_NAME}...")
        if mw.col is None:
            raise Exception("mw.col is none")
        model = mw.col.models.by_name(MODEL_NAME)
        if not model:
            showInfo(
                f"Model (Note Type) '{MODEL_NAME}' does not exist! Please Sync first!"
            )
            return

        logger.info(f"model: {json.dumps(model)}")
        logger.info("Checking fields...")
        self.logHandler.flush()
        ok, unknown_fields, missing_fields = checkModelFields(model)
        if not ok and missing_fields:
            if not askUser(
                "Model fields are not as expected. Merge now?", defaultno=True
            ):
                logger.info("Aborted")
                self.logHandler.flush()
                return
            mergeModelFields(model)

        logger.info("Checking card templates...")
        currentConfig = self.getAndSaveCurrentConfig()
        fg = self.getFieldGroup(currentConfig)
        if checkModelCardTemplates(model, fg) and checkModelCardCSS(model):
            logger.info("No changes detected.")
            self.logHandler.flush()
            tooltip("No changes detected.")
            return

        else:
            if not askUser(
                "Model card templates or CSS have been changed. Would you like to reset to default?",
                defaultno=True,
            ):
                logger.info("Aborted")
                self.logHandler.flush()
                return
            logger.info(f"Resetting card templates for model {MODEL_NAME}...")
            resetModelCardTemplates(model, fg)
            logger.info("Done!")
            self.logHandler.flush()
            tooltip("Reset complete.")
