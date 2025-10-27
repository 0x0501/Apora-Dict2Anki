# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'loginDialog.ui'
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
    QApplication,
    QDialog,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        if not LoginDialog.objectName():
            LoginDialog.setObjectName("LoginDialog")
        LoginDialog.resize(505, 480)
        self.gridLayout = QGridLayout(LoginDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.reloadBtn = QPushButton(LoginDialog)
        self.reloadBtn.setObjectName("reloadBtn")

        self.gridLayout.addWidget(self.reloadBtn, 0, 1, 1, 1)

        self.pageContainer = QVBoxLayout()
        self.pageContainer.setObjectName("pageContainer")

        self.gridLayout.addLayout(self.pageContainer, 1, 0, 1, 2)

        self.address = QLineEdit(LoginDialog)
        self.address.setObjectName("address")
        self.address.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.address, 0, 0, 1, 1)

        self.retranslateUi(LoginDialog)

        QMetaObject.connectSlotsByName(LoginDialog)

    # setupUi

    def retranslateUi(self, LoginDialog):
        LoginDialog.setWindowTitle(
            QCoreApplication.translate("LoginDialog", "Login", None)
        )
        self.reloadBtn.setText(
            QCoreApplication.translate("LoginDialog", "reload", None)
        )

    # retranslateUi
