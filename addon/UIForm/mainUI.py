# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainUI.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from . import icons_rc
from PyQt6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QTextBrowser,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(613, 725)
        self.main_layout = QVBoxLayout(Dialog)
        self.main_layout.setObjectName("main_layout")
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setAutoFillBackground(False)
        self.mainTab = QWidget()
        self.mainTab.setObjectName("mainTab")
        self.gridLayout_4 = QGridLayout(self.mainTab)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.dictionaryLayout = QHBoxLayout()
        self.dictionaryLayout.setObjectName("dictionaryLayout")
        self.dictionaryLabel = QLabel(self.mainTab)
        self.dictionaryLabel.setObjectName("dictionaryLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.dictionaryLabel.sizePolicy().hasHeightForWidth()
        )
        self.dictionaryLabel.setSizePolicy(sizePolicy1)

        self.dictionaryLayout.addWidget(self.dictionaryLabel)

        self.dictionaryComboBox = QComboBox(self.mainTab)
        self.dictionaryComboBox.setObjectName("dictionaryComboBox")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.dictionaryComboBox.sizePolicy().hasHeightForWidth()
        )
        self.dictionaryComboBox.setSizePolicy(sizePolicy2)

        self.dictionaryLayout.addWidget(self.dictionaryComboBox)

        self.gridLayout_4.addLayout(self.dictionaryLayout, 2, 0, 1, 5)

        self.pullRemoteWordsBtn = QPushButton(self.mainTab)
        self.pullRemoteWordsBtn.setObjectName("pullRemoteWordsBtn")

        self.gridLayout_4.addWidget(self.pullRemoteWordsBtn, 5, 0, 1, 1)

        self.deckLayout = QHBoxLayout()
        self.deckLayout.setObjectName("deckLayout")
        self.deckLabel = QLabel(self.mainTab)
        self.deckLabel.setObjectName("deckLabel")
        sizePolicy1.setHeightForWidth(self.deckLabel.sizePolicy().hasHeightForWidth())
        self.deckLabel.setSizePolicy(sizePolicy1)

        self.deckLayout.addWidget(self.deckLabel)

        self.deckComboBox = QComboBox(self.mainTab)
        self.deckComboBox.setObjectName("deckComboBox")
        sizePolicy2.setHeightForWidth(
            self.deckComboBox.sizePolicy().hasHeightForWidth()
        )
        self.deckComboBox.setSizePolicy(sizePolicy2)
        self.deckComboBox.setEditable(True)

        self.deckLayout.addWidget(self.deckComboBox)

        self.gridLayout_4.addLayout(self.deckLayout, 1, 0, 1, 5)

        self.queryAndLanguageLayout = QHBoxLayout()
        self.queryAndLanguageLayout.setObjectName("queryAndLanguageLayout")
        self.apiLayout = QHBoxLayout()
        self.apiLayout.setObjectName("apiLayout")
        self.apiLabel = QLabel(self.mainTab)
        self.apiLabel.setObjectName("apiLabel")
        sizePolicy1.setHeightForWidth(self.apiLabel.sizePolicy().hasHeightForWidth())
        self.apiLabel.setSizePolicy(sizePolicy1)

        self.apiLayout.addWidget(self.apiLabel)

        self.apiComboBox = QComboBox(self.mainTab)
        self.apiComboBox.setObjectName("apiComboBox")
        sizePolicy2.setHeightForWidth(self.apiComboBox.sizePolicy().hasHeightForWidth())
        self.apiComboBox.setSizePolicy(sizePolicy2)
        self.apiComboBox.setEditable(False)

        self.apiLayout.addWidget(self.apiComboBox)

        self.queryAndLanguageLayout.addLayout(self.apiLayout)

        self.languageLayout = QHBoxLayout()
        self.languageLayout.setObjectName("languageLayout")
        self.languageLabel = QLabel(self.mainTab)
        self.languageLabel.setObjectName("languageLabel")
        sizePolicy1.setHeightForWidth(
            self.languageLabel.sizePolicy().hasHeightForWidth()
        )
        self.languageLabel.setSizePolicy(sizePolicy1)

        self.languageLayout.addWidget(self.languageLabel)

        self.languageComboBox = QComboBox(self.mainTab)
        self.languageComboBox.setObjectName("languageComboBox")

        self.languageLayout.addWidget(self.languageComboBox)

        self.queryAndLanguageLayout.addLayout(self.languageLayout)

        self.gridLayout_4.addLayout(self.queryAndLanguageLayout, 3, 0, 1, 5)

        self.btnSync = QPushButton(self.mainTab)
        self.btnSync.setObjectName("btnSync")
        self.btnSync.setEnabled(False)

        self.gridLayout_4.addWidget(self.btnSync, 5, 4, 1, 1)

        self.btnImportFromFiles = QToolButton(self.mainTab)
        self.btnImportFromFiles.setObjectName("btnImportFromFiles")

        self.gridLayout_4.addWidget(self.btnImportFromFiles, 5, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(self.mainTab)
        self.label.setObjectName("label")

        self.verticalLayout.addWidget(self.label)

        self.newWordListWidget = QListWidget(self.mainTab)
        self.newWordListWidget.setObjectName("newWordListWidget")
        self.newWordListWidget.setAlternatingRowColors(True)
        self.newWordListWidget.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )

        self.verticalLayout.addWidget(self.newWordListWidget)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(
            QLayout.SizeConstraint.SetDefaultConstraint
        )
        self.label_2 = QLabel(self.mainTab)
        self.label_2.setObjectName("label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.needDeleteWordListWidget = QListWidget(self.mainTab)
        self.needDeleteWordListWidget.setObjectName("needDeleteWordListWidget")
        self.needDeleteWordListWidget.setAlternatingRowColors(True)

        self.verticalLayout_2.addWidget(self.needDeleteWordListWidget)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.gridLayout_4.addLayout(self.horizontalLayout, 4, 0, 1, 5)

        self.queryBtn = QPushButton(self.mainTab)
        self.queryBtn.setObjectName("queryBtn")
        self.queryBtn.setEnabled(False)

        self.gridLayout_4.addWidget(self.queryBtn, 5, 3, 1, 1)

        self.tabWidget.addTab(self.mainTab, "")
        self.settingTab = QWidget()
        self.settingTab.setObjectName("settingTab")
        self.gridLayout_2 = QGridLayout(self.settingTab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.cardConfigGroupBox = QGroupBox(self.settingTab)
        self.cardConfigGroupBox.setObjectName("cardConfigGroupBox")
        sizePolicy.setHeightForWidth(
            self.cardConfigGroupBox.sizePolicy().hasHeightForWidth()
        )
        self.cardConfigGroupBox.setSizePolicy(sizePolicy)
        self.gridLayout_6 = QGridLayout(self.cardConfigGroupBox)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.enableTermHighlight = QCheckBox(self.cardConfigGroupBox)
        self.enableTermHighlight.setObjectName("enableTermHighlight")

        self.gridLayout_6.addWidget(self.enableTermHighlight, 1, 0, 1, 1)

        self.USSpeakingRadioButton = QRadioButton(self.cardConfigGroupBox)
        self.SpeakingVariantRadioButtonGroup = QButtonGroup(Dialog)
        self.SpeakingVariantRadioButtonGroup.setObjectName(
            "SpeakingVariantRadioButtonGroup"
        )
        self.SpeakingVariantRadioButtonGroup.addButton(self.USSpeakingRadioButton)
        self.USSpeakingRadioButton.setObjectName("USSpeakingRadioButton")
        self.USSpeakingRadioButton.setChecked(True)

        self.gridLayout_6.addWidget(self.USSpeakingRadioButton, 2, 0, 1, 1)

        self.label_4 = QLabel(self.cardConfigGroupBox)
        self.label_4.setObjectName("label_4")

        self.gridLayout_6.addWidget(self.label_4, 3, 0, 1, 1)

        self.enableContextCheckBox = QCheckBox(self.cardConfigGroupBox)
        self.enableContextCheckBox.setObjectName("enableContextCheckBox")
        self.enableContextCheckBox.setChecked(True)

        self.gridLayout_6.addWidget(self.enableContextCheckBox, 0, 0, 1, 1)

        self.disableSpeakingRadioButton = QRadioButton(self.cardConfigGroupBox)
        self.SpeakingRadioButtonGroup = QButtonGroup(Dialog)
        self.SpeakingRadioButtonGroup.setObjectName("SpeakingRadioButtonGroup")
        self.SpeakingRadioButtonGroup.addButton(self.disableSpeakingRadioButton)
        self.disableSpeakingRadioButton.setObjectName("disableSpeakingRadioButton")
        self.disableSpeakingRadioButton.setEnabled(True)

        self.gridLayout_6.addWidget(self.disableSpeakingRadioButton, 1, 1, 1, 1)

        self.termSpeakingRadioButton = QRadioButton(self.cardConfigGroupBox)
        self.SpeakingRadioButtonGroup.addButton(self.termSpeakingRadioButton)
        self.termSpeakingRadioButton.setObjectName("termSpeakingRadioButton")
        self.termSpeakingRadioButton.setChecked(False)

        self.gridLayout_6.addWidget(self.termSpeakingRadioButton, 1, 3, 1, 1)

        self.enableChineseCheckBox = QCheckBox(self.cardConfigGroupBox)
        self.enableChineseCheckBox.setObjectName("enableChineseCheckBox")

        self.gridLayout_6.addWidget(self.enableChineseCheckBox, 0, 1, 1, 1)

        self.contextTranslation = QCheckBox(self.cardConfigGroupBox)
        self.contextTranslation.setObjectName("contextTranslation")

        self.gridLayout_6.addWidget(self.contextTranslation, 3, 3, 1, 1)

        self.GBSpeakingRadioButton = QRadioButton(self.cardConfigGroupBox)
        self.SpeakingVariantRadioButtonGroup.addButton(self.GBSpeakingRadioButton)
        self.GBSpeakingRadioButton.setObjectName("GBSpeakingRadioButton")
        self.GBSpeakingRadioButton.setChecked(False)

        self.gridLayout_6.addWidget(self.GBSpeakingRadioButton, 2, 1, 1, 1)

        self.enableAddPartOfSpeechToTag = QCheckBox(self.cardConfigGroupBox)
        self.enableAddPartOfSpeechToTag.setObjectName("enableAddPartOfSpeechToTag")

        self.gridLayout_6.addWidget(self.enableAddPartOfSpeechToTag, 0, 3, 1, 1)

        self.contextDifficultyComboBox = QComboBox(self.cardConfigGroupBox)
        self.contextDifficultyComboBox.addItem("")
        self.contextDifficultyComboBox.addItem("")
        self.contextDifficultyComboBox.addItem("")
        self.contextDifficultyComboBox.setObjectName("contextDifficultyComboBox")
        sizePolicy3 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(
            self.contextDifficultyComboBox.sizePolicy().hasHeightForWidth()
        )
        self.contextDifficultyComboBox.setSizePolicy(sizePolicy3)
        self.contextDifficultyComboBox.setFrame(True)

        self.gridLayout_6.addWidget(self.contextDifficultyComboBox, 3, 1, 1, 1)

        self.contextSpeakingRadioButton = QRadioButton(self.cardConfigGroupBox)
        self.SpeakingRadioButtonGroup.addButton(self.contextSpeakingRadioButton)
        self.contextSpeakingRadioButton.setObjectName("contextSpeakingRadioButton")
        self.contextSpeakingRadioButton.setChecked(True)

        self.gridLayout_6.addWidget(self.contextSpeakingRadioButton, 2, 3, 1, 1)

        self.cardSettingDescription = QTextBrowser(self.cardConfigGroupBox)
        self.cardSettingDescription.setObjectName("cardSettingDescription")
        self.cardSettingDescription.setMinimumSize(QSize(0, 45))
        self.cardSettingDescription.setMaximumSize(QSize(16777215, 50))

        self.gridLayout_6.addWidget(self.cardSettingDescription, 4, 0, 1, 4)

        self.gridLayout_2.addWidget(self.cardConfigGroupBox, 4, 0, 1, 2)

        self.credentialGroupBox = QGroupBox(self.settingTab)
        self.credentialGroupBox.setObjectName("credentialGroupBox")
        self.gridLayout_3 = QGridLayout(self.credentialGroupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.currentDictionaryLabel = QLabel(self.credentialGroupBox)
        self.currentDictionaryLabel.setObjectName("currentDictionaryLabel")
        sizePolicy2.setHeightForWidth(
            self.currentDictionaryLabel.sizePolicy().hasHeightForWidth()
        )
        self.currentDictionaryLabel.setSizePolicy(sizePolicy2)

        self.gridLayout_3.addWidget(self.currentDictionaryLabel, 0, 0, 1, 2)

        self.usernameLabel = QLabel(self.credentialGroupBox)
        self.usernameLabel.setObjectName("usernameLabel")

        self.gridLayout_3.addWidget(self.usernameLabel, 1, 0, 1, 1)

        self.usernameLineEdit = QLineEdit(self.credentialGroupBox)
        self.usernameLineEdit.setObjectName("usernameLineEdit")

        self.gridLayout_3.addWidget(self.usernameLineEdit, 1, 1, 1, 1)

        self.passwordLabel = QLabel(self.credentialGroupBox)
        self.passwordLabel.setObjectName("passwordLabel")

        self.gridLayout_3.addWidget(self.passwordLabel, 1, 2, 1, 1)

        self.passwordLineEdit = QLineEdit(self.credentialGroupBox)
        self.passwordLineEdit.setObjectName("passwordLineEdit")

        self.gridLayout_3.addWidget(self.passwordLineEdit, 1, 3, 1, 1)

        self.cookieLabel = QLabel(self.credentialGroupBox)
        self.cookieLabel.setObjectName("cookieLabel")
        sizePolicy1.setHeightForWidth(self.cookieLabel.sizePolicy().hasHeightForWidth())
        self.cookieLabel.setSizePolicy(sizePolicy1)
        self.cookieLabel.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.gridLayout_3.addWidget(self.cookieLabel, 2, 0, 1, 1)

        self.cookieLineEdit = QLineEdit(self.credentialGroupBox)
        self.cookieLineEdit.setObjectName("cookieLineEdit")
        self.cookieLineEdit.setClearButtonEnabled(True)

        self.gridLayout_3.addWidget(self.cookieLineEdit, 2, 1, 1, 3)

        self.gridLayout_2.addWidget(self.credentialGroupBox, 0, 0, 1, 2)

        self.defaultConfigGroupBox = QGroupBox(self.settingTab)
        self.defaultConfigGroupBox.setObjectName("defaultConfigGroupBox")
        self.gridLayout = QGridLayout(self.defaultConfigGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.syncTemplatesCheckbox = QCheckBox(self.defaultConfigGroupBox)
        self.syncTemplatesCheckbox.setObjectName("syncTemplatesCheckbox")
        self.syncTemplatesCheckbox.setChecked(True)

        self.gridLayout.addWidget(self.syncTemplatesCheckbox, 0, 0, 1, 1)

        self.gridLayout_2.addWidget(self.defaultConfigGroupBox, 3, 0, 1, 2)

        self.aporaCredentialGroupBox = QGroupBox(self.settingTab)
        self.aporaCredentialGroupBox.setObjectName("aporaCredentialGroupBox")
        self.gridLayout_10 = QGridLayout(self.aporaCredentialGroupBox)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.AporaTokenLabel = QLabel(self.aporaCredentialGroupBox)
        self.AporaTokenLabel.setObjectName("AporaTokenLabel")
        sizePolicy1.setHeightForWidth(
            self.AporaTokenLabel.sizePolicy().hasHeightForWidth()
        )
        self.AporaTokenLabel.setSizePolicy(sizePolicy1)
        self.AporaTokenLabel.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.gridLayout_10.addWidget(self.AporaTokenLabel, 0, 0, 1, 1)

        self.AporaAPITokenLineEdit = QLineEdit(self.aporaCredentialGroupBox)
        self.AporaAPITokenLineEdit.setObjectName("AporaAPITokenLineEdit")
        self.AporaAPITokenLineEdit.setEnabled(True)
        self.AporaAPITokenLineEdit.setClearButtonEnabled(True)

        self.gridLayout_10.addWidget(self.AporaAPITokenLineEdit, 0, 1, 1, 2)

        self.AporaAPITokenDescription = QTextBrowser(self.aporaCredentialGroupBox)
        self.AporaAPITokenDescription.setObjectName("AporaAPITokenDescription")
        self.AporaAPITokenDescription.setMaximumSize(QSize(16777215, 50))
        self.AporaAPITokenDescription.setStyleSheet("")
        self.AporaAPITokenDescription.setOpenExternalLinks(True)

        self.gridLayout_10.addWidget(self.AporaAPITokenDescription, 1, 0, 1, 3)

        self.gridLayout_2.addWidget(self.aporaCredentialGroupBox, 1, 0, 1, 2)

        self.tabWidget.addTab(self.settingTab, "")
        self.utilitiesTab = QWidget()
        self.utilitiesTab.setObjectName("utilitiesTab")
        self.gridLayout_5 = QGridLayout(self.utilitiesTab)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.dangerZoneGroupBox = QGroupBox(self.utilitiesTab)
        self.dangerZoneGroupBox.setObjectName("dangerZoneGroupBox")
        self.dangerZoneGroupBox.setStyleSheet("color: red")
        self.gridLayout_8 = QGridLayout(self.dangerZoneGroupBox)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.btnBackwardTemplate = QPushButton(self.dangerZoneGroupBox)
        self.btnBackwardTemplate.setObjectName("btnBackwardTemplate")

        self.gridLayout_8.addWidget(self.btnBackwardTemplate, 0, 0, 1, 1)

        self.btnCheckTemplates = QPushButton(self.dangerZoneGroupBox)
        self.btnCheckTemplates.setObjectName("btnCheckTemplates")

        self.gridLayout_8.addWidget(self.btnCheckTemplates, 0, 1, 1, 1)

        self.gridLayout_5.addWidget(self.dangerZoneGroupBox, 1, 0, 1, 1)

        self.utilitiesGroupBox = QGroupBox(self.utilitiesTab)
        self.utilitiesGroupBox.setObjectName("utilitiesGroupBox")
        self.gridLayout_7 = QGridLayout(self.utilitiesGroupBox)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.btnDownloadMissingAssets = QPushButton(self.utilitiesGroupBox)
        self.btnDownloadMissingAssets.setObjectName("btnDownloadMissingAssets")

        self.gridLayout_7.addWidget(self.btnDownloadMissingAssets, 0, 0, 1, 1)

        self.btnFillMissingValues = QPushButton(self.utilitiesGroupBox)
        self.btnFillMissingValues.setObjectName("btnFillMissingValues")

        self.gridLayout_7.addWidget(self.btnFillMissingValues, 0, 1, 1, 1)

        self.btnExportAudio = QPushButton(self.utilitiesGroupBox)
        self.btnExportAudio.setObjectName("btnExportAudio")

        self.gridLayout_7.addWidget(self.btnExportAudio, 1, 0, 1, 1)

        self.gridLayout_5.addWidget(self.utilitiesGroupBox, 0, 0, 1, 1)

        self.tabWidget.addTab(self.utilitiesTab, "")

        self.main_layout.addWidget(self.tabWidget)

        self.progressBar = QProgressBar(Dialog)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)

        self.main_layout.addWidget(self.progressBar)

        self.logTextLabel = QLabel(Dialog)
        self.logTextLabel.setObjectName("logTextLabel")

        self.main_layout.addWidget(self.logTextLabel)

        self.logTextBox = QPlainTextEdit(Dialog)
        self.logTextBox.setObjectName("logTextBox")
        self.logTextBox.setUndoRedoEnabled(False)
        self.logTextBox.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

        self.main_layout.addWidget(self.logTextBox)

        self.FooterGroup = QHBoxLayout()
        self.FooterGroup.setObjectName("FooterGroup")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.FooterGroup.addItem(self.horizontalSpacer)

        self.saveSettingsButton = QPushButton(Dialog)
        self.saveSettingsButton.setObjectName("saveSettingsButton")
        self.saveSettingsButton.setMinimumSize(QSize(100, 0))

        self.FooterGroup.addWidget(self.saveSettingsButton)

        self.main_layout.addLayout(self.FooterGroup)

        self.retranslateUi(Dialog)

        self.tabWidget.setCurrentIndex(0)
        self.contextDifficultyComboBox.setCurrentIndex(1)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Dialog", None))
        self.dictionaryLabel.setText(
            QCoreApplication.translate("Dialog", "\u8bcd\u5178", None)
        )
        self.pullRemoteWordsBtn.setText(
            QCoreApplication.translate("Dialog", "\u62c9\u53d6\u5355\u8bcd\u8868", None)
        )
        self.deckLabel.setText(
            QCoreApplication.translate("Dialog", "\u724c\u7ec4", None)
        )
        self.apiLabel.setText(
            QCoreApplication.translate("Dialog", "\u67e5\u8be2", None)
        )
        self.languageLabel.setText(
            QCoreApplication.translate("Dialog", "\u8bed\u8a00", None)
        )
        self.btnSync.setText(QCoreApplication.translate("Dialog", "\u540c\u6b65", None))
        # if QT_CONFIG(tooltip)
        self.btnImportFromFiles.setToolTip(
            QCoreApplication.translate(
                "Dialog",
                "Import words from txt files. (Use Tabs to separate the fields)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnImportFromFiles.setText(
            QCoreApplication.translate("Dialog", "...", None)
        )
        self.label.setText(
            QCoreApplication.translate("Dialog", "\u65b0\u5355\u8bcd", None)
        )
        self.label_2.setText(
            QCoreApplication.translate("Dialog", "\u5f85\u5220\u9664", None)
        )
        self.queryBtn.setText(
            QCoreApplication.translate(
                "Dialog", "\u83b7\u53d6\u8bcd\u5178\u6570\u636e", None
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.mainTab),
            QCoreApplication.translate("Dialog", "\u540c\u6b65", None),
        )
        self.cardConfigGroupBox.setTitle(
            QCoreApplication.translate("Dialog", "\u5361\u7247\u8bbe\u7f6e", None)
        )
        self.enableTermHighlight.setText(
            QCoreApplication.translate(
                "Dialog", "Context\u4e2d\u9ad8\u4eae\u5355\u8bcd/\u77ed\u8bed", None
            )
        )
        self.USSpeakingRadioButton.setText(
            QCoreApplication.translate(
                "Dialog", "\u7f8e\u5f0f\u53d1\u97f3\uff08US\uff09", None
            )
        )
        self.label_4.setText(
            QCoreApplication.translate(
                "Dialog", "Context\u4e0a\u4e0b\u6587\u96be\u5ea6", None
            )
        )
        self.enableContextCheckBox.setText(
            QCoreApplication.translate(
                "Dialog", "\u5355\u8bcd\u4e0a\u4e0b\u6587\uff08Context\uff09", None
            )
        )
        self.disableSpeakingRadioButton.setText(
            QCoreApplication.translate("Dialog", "\u65e0\u53d1\u97f3", None)
        )
        self.termSpeakingRadioButton.setText(
            QCoreApplication.translate(
                "Dialog", "\u5355\u8bcd\u53d1\u97f3\uff08\u4e0d\u63a8\u8350\uff09", None
            )
        )
        self.enableChineseCheckBox.setText(
            QCoreApplication.translate("Dialog", "\u4e2d\u6587\u91ca\u4e49", None)
        )
        self.contextTranslation.setText(
            QCoreApplication.translate(
                "Dialog",
                "\u4e0a\u4e0b\u6587\u7ffb\u8bd1\uff08Context Translation\uff09",
                None,
            )
        )
        self.GBSpeakingRadioButton.setText(
            QCoreApplication.translate(
                "Dialog", "\u82f1\u5f0f\u53d1\u97f3\uff08GB\uff09", None
            )
        )
        self.enableAddPartOfSpeechToTag.setText(
            QCoreApplication.translate(
                "Dialog", "\u6dfb\u52a0\u8bcd\u6027\u5230Anki\u6807\u7b7e", None
            )
        )
        self.contextDifficultyComboBox.setItemText(
            0,
            QCoreApplication.translate("Dialog", "\u7b80\u5355\uff08Easy\uff09", None),
        )
        self.contextDifficultyComboBox.setItemText(
            1,
            QCoreApplication.translate(
                "Dialog", "\u4e2d\u7b49\uff08Normal\uff09", None
            ),
        )
        self.contextDifficultyComboBox.setItemText(
            2,
            QCoreApplication.translate(
                "Dialog", "\u4e13\u4e1a\uff08Professional\uff09", None
            ),
        )

        self.contextSpeakingRadioButton.setText(
            QCoreApplication.translate(
                "Dialog", "\u53e5\u5b50\u53d1\u97f3\uff08\u63a8\u8350\uff09", None
            )
        )
        self.cardSettingDescription.setHtml(
            QCoreApplication.translate(
                "Dialog",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "hr { height: 1px; border-width: 0; }\n"
                'li.unchecked::marker { content: "\\2610"; }\n'
                'li.checked::marker { content: "\\2612"; }\n'
                "</style></head><body style=\" font-family:'Microsoft YaHei UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                '<p align="justify" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">\u6ce8\u610f\uff1a\u5355\u8bcd\u53d1\u97f3\uff08Term Speaking\uff09\u548c\u53e5\u5b50\u53d1\u97f3\uff08Context Speaking\uff09\u4e0d\u80fd\u540c\u65f6\u5f00\u542f\u3002\u5efa\u8bae<span style=" font-weight:700;">\u4f18\u5148\u4f7f\u7528\u53e5\u5b50\u53d1\u97f3</span>\uff0cTTS\u6a21\u578b\u5728\u8f93\u5165\u8bcd\u6c47\u8f83\u5c11\u65f6\u53ef\u80fd\u51fa\u73b0\u5f02\u5e38\u3002'
                "</p></body></html>",
                None,
            )
        )
        self.credentialGroupBox.setTitle(
            QCoreApplication.translate(
                "Dialog", "\u8bcd\u5178\u8d26\u53f7\u8bbe\u7f6e", None
            )
        )
        self.currentDictionaryLabel.setText(
            QCoreApplication.translate(
                "Dialog", "\u5f53\u524d\u9009\u62e9\u8bcd\u5178: ", None
            )
        )
        self.usernameLabel.setText(
            QCoreApplication.translate("Dialog", "\u8d26\u53f7", None)
        )
        self.passwordLabel.setText(
            QCoreApplication.translate("Dialog", "\u5bc6\u7801", None)
        )
        self.cookieLabel.setText(QCoreApplication.translate("Dialog", "Cookie", None))
        self.cookieLineEdit.setPlaceholderText(
            QCoreApplication.translate("Dialog", "\u9009\u586b", None)
        )
        self.defaultConfigGroupBox.setTitle(
            QCoreApplication.translate("Dialog", "\u540c\u6b65\u8bbe\u7f6e", None)
        )
        self.syncTemplatesCheckbox.setText(
            QCoreApplication.translate("Dialog", "\u540c\u6b65\u6a21\u7248", None)
        )
        self.aporaCredentialGroupBox.setTitle(
            QCoreApplication.translate("Dialog", "Apora\u8d26\u53f7\u8bbe\u7f6e", None)
        )
        self.AporaTokenLabel.setText(
            QCoreApplication.translate("Dialog", "Apora API Token", None)
        )
        self.AporaAPITokenLineEdit.setPlaceholderText(
            QCoreApplication.translate("Dialog", "\u5fc5\u586b", None)
        )
        self.AporaAPITokenDescription.setHtml(
            QCoreApplication.translate(
                "Dialog",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "hr { height: 1px; border-width: 0; }\n"
                'li.unchecked::marker { content: "\\2610"; }\n'
                'li.checked::marker { content: "\\2612"; }\n'
                "</style></head><body style=\" font-family:'Microsoft YaHei UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Token\u9700\u8981\u4eceApora\u5b98\u7f51<a href="https://apora.sumku.cc"><span style=" text-decoration: underline; color:#134958;">https://apora.sumku.cc</span></a>\u83b7\u53d6\u3002\u6b65\u9aa4\uff1a\u767b\u9646Apora\u8d26\u53f7\u3002\u8fdb\u5165\u7ba1\u7406\u540e\u53f0\uff0c\u70b9\u51fbToken\u6309\u94ae\u751f\u6210\u3002\u8bf7\u4fdd\u7ba1\u597d\u60a8\u7684Token\uff0c\u4e0d\u8981\u6cc4\u9732'
                "\u7ed9\u4ed6\u4eba\u3002</p></body></html>",
                None,
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.settingTab),
            QCoreApplication.translate("Dialog", "\u8bbe\u7f6e", None),
        )
        self.dangerZoneGroupBox.setTitle(
            QCoreApplication.translate("Dialog", "Danger Zone", None)
        )
        self.btnBackwardTemplate.setText(
            QCoreApplication.translate("Dialog", "Add/Delete Backwards Template", None)
        )
        self.btnCheckTemplates.setText(
            QCoreApplication.translate("Dialog", "Check Card Templates", None)
        )
        self.utilitiesGroupBox.setTitle(
            QCoreApplication.translate("Dialog", "Utilities", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnDownloadMissingAssets.setToolTip(
            QCoreApplication.translate(
                "Dialog",
                "Check existing notes and download missing assets (images, audio files, etc.)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnDownloadMissingAssets.setText(
            QCoreApplication.translate("Dialog", "Download Missing Assets", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnFillMissingValues.setToolTip(
            QCoreApplication.translate(
                "Dialog", "Check existing notes and fill missing field values", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnFillMissingValues.setText(
            QCoreApplication.translate("Dialog", "Fill Missing Values", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnExportAudio.setToolTip(
            QCoreApplication.translate(
                "Dialog",
                "Export all words in selected deck into a single audio file. (macOS only)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnExportAudio.setText(
            QCoreApplication.translate("Dialog", "Export Audio (macOS only)", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.utilitiesTab),
            QCoreApplication.translate("Dialog", "\u5de5\u5177", None),
        )
        self.logTextLabel.setText(
            QCoreApplication.translate("Dialog", "\u65e5\u5fd7\u8f93\u51fa", None)
        )
        self.logTextBox.setDocumentTitle("")
        self.saveSettingsButton.setText(
            QCoreApplication.translate("Dialog", "\u4fdd\u5b58\u8bbe\u7f6e", None)
        )

    # retranslateUi
