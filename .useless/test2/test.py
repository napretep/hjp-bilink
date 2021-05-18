import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QShortcutEvent, QKeySequence
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QLineEdit, QShortcut,
                             QMainWindow, QPushButton, QToolBar, QDialog, QHBoxLayout)
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5 import QtWebEngineWidgets, QtWidgets


class testwindow(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('PySide2 WebEngineWidgets Example')

        # self.toolBar = QToolBar()
        # self.addToolBar(self.toolBar)
        # self.backButton = QPushButton()
        # self.backButton.setIcon(QIcon(':/qt-project.org/styles/commonstyle/images/left-32.png'))
        # self.backButton.clicked.connect(self.back)
        # # self.toolBar.addWidget(self.backButton)
        # self.forwardButton = QPushButton()
        # self.forwardButton.setIcon(QIcon(':/qt-project.org/styles/commonstyle/images/right-32.png'))
        # self.forwardButton.clicked.connect(self.forward)
        # self.toolBar.addWidget(self.forwardButton)
        # QShortcut(QKeySequence("Ct"),self,activated= lambda :self.back())
        # self.addressLineEdit = QLineEdit()
        # self.addressLineEdit.returnPressed.connect(self.load)
        # self.toolBar.addWidget(self.addressLineEdit)
        self.webEngineView = QWebEngineView()
        settings = self.webEngineView.settings()
        settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PdfViewerEnabled, True)
        settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.FullScreenSupportEnabled, True)
        # self.setCentralWidget(self.webEngineView)
        initialUrl = r'file:///G:/备份/数学书大全/微分方程/算子法在处理线性微分方程中的应用.pdf#page=2'
        # self.addressLineEdit.setText(initialUrl)
        self.webEngineView.load(QUrl(initialUrl))
        # self.webEngineView.page().runJavaScript("window.viewer.viewport_.goToPage(20)")
        # self.webEngineView.page().titleChanged.connect(self.setWindowTitle)
        # self.webEngineView.page().urlChanged.connect(self.urlChanged)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addWidget(self.webEngineView)
        self.show()

    # def load(self):
    #     url = QUrl.fromUserInput(self.addressLineEdit.text())
    #     if url.isValid():
    #         self.webEngineView.load(url)
    #
    # def back(self):
    #     self.webEngineView.page().triggerAction(QWebEnginePage.Back)

    # def forward(self):
    #     self.webEngineView.page().triggerAction(QWebEnginePage.Forward)
    #
    # def urlChanged(self, url):
    #     self.addressLineEdit.setText(url.toString())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = testwindow()
    # availableGeometry = app.desktop().availableGeometry(mainWin)
    # mainWin.resize(availableGeometry.width() * 2 / 3, availableGeometry.height() * 2 / 3)
    mainWin.show()
    sys.exit(app.exec_())
