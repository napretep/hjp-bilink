import json

from PyQt5 import QtGui
from PyQt5.QtGui import QTextFormat, QIcon
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QToolButton, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar, \
    QGridLayout
from PyQt5.QtCore import Qt

from ..tools import events, funcs, objs, ALL


class CardinfosPreviewer(QDialog):
    pass


class ClipperExecuteProgresser(QDialog):
    def __init__(self, cardlist=None):
        super().__init__(parent=cardlist)
        self.cardlist = cardlist
        self.prepare_progress = objs.ProgressBarBlackFont(self)
        # self.curCard_progress = objs.ProgressBarBlackFont(self)
        # self.allCard_progress = objs.ProgressBarBlackFont(self)
        self.return_button = QToolButton(self)
        self.close_button = QToolButton(self)
        self.stop_button = QToolButton(self)
        self.init_UI()
        self.init_events()

    def init_job(self):
        from .. import RightSideBar_
        self.job = RightSideBar_.FinalExecution_masterJob(cardlist=self.cardlist)
        self.job.on_job_done.connect(self.on_masterjob_done_handle)
        self.job.on_job_progress.connect(self.progress_dispatcher)
        self.job.start()

    def on_masterjob_done_handle(self, timestamp):
        e = events.AnkiBrowserActivateEvent
        ALL.signals.on_anki_browser_activate.emit(
            e(eventType=e.ClipperTaskFinishedType, sender=self, data=timestamp)
        )
        self.prepare_progress.setFormat("任务完成/task complete %p%")

    def progress_dispatcher(self, data):
        status = ["提取clipbox信息/extract clipbox info %p%",
                  "创建卡片/create new card %p%",
                  "插入卡片字段/insert into card field %p%",
                  "插入数据库/insert into database %p%",
                  "创建png图片/create png %p%"]
        self.prepare_progress.setValue(data[1])
        self.prepare_progress.setFormat(status[data[0]])

    def init_UI(self):
        self.setFixedWidth(400)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        # self.prepare_progress.setFormat("预备工作/prepare work progress %p%")
        # self.curCard_progress.setFormat(("当前卡片进度/current card progress %p%"))
        # self.allCard_progress.setFormat("全部卡片进度/all cards progress %p%")
        # self.allCard_progress.setValue(10)
        # self.curCard_progress.setValue(10)
        self.return_button.setIcon(QIcon(objs.SrcAdmin.imgDir.goback))
        self.close_button.setIcon(QIcon(objs.SrcAdmin.imgDir.close))
        self.stop_button.setIcon(QIcon(objs.SrcAdmin.imgDir.stop))
        self.return_button.setToolTip("回到clipper主窗口\ngoback to clipper window")
        self.stop_button.setToolTip("终止任务\nterminate the task")
        self.close_button.setToolTip("关闭整个clipper工作室\nclose the whole pdf-clipper-workshop")
        g_layout = QGridLayout(self)

        g_layout.addWidget(self.prepare_progress, 0, 0, 1, 4)
        g_layout.addWidget(self.return_button, 1, 1)
        g_layout.addWidget(self.stop_button, 1, 2)
        g_layout.addWidget(self.close_button, 1, 3)
        self.setLayout(g_layout)

    def init_events(self):
        self.return_button.clicked.connect(self.on_return_button_clicked_handle)
        self.close_button.clicked.connect(self.on_close_button_clicked_handle)
        self.stop_button.clicked.connect(self.on_stop_button_clicked_handle)
        ALL.signals.on_ClipperExecuteProgresser_show.connect(self.on_ClipperExecuteProgresser_show_handle)
        # self.setShortcutEnabled()
        pass

    def on_close_button_clicked_handle(self):
        self.cardlist.rightsidebar.clipper.close()
        self.close()

    def on_stop_button_clicked_handle(self):
        """终止任务"""

    def on_return_button_clicked_handle(self):
        self.close()

    def on_ClipperExecuteProgresser_show_handle(self):
        self.init_job()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        """阻止所有键盘事件"""
        pass

    pass


class CardinfosPreviewConfirm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.button_ok = QToolButton(self)
        self.button_no = QToolButton(self)
        self.question_label = QLabel(self)
        self.init_UI()
        # self.show()

    def init_UI(self):
        self.setWindowFlag(Qt.Tool)
        self.question_label.setText("执行操作前是否预览卡片?\ndo you want to preview the card infos before execution?")
        self.button_ok.setText("ok")
        self.button_no.setText("no")
        v_box = QVBoxLayout(self)
        h_box = QHBoxLayout()
        h_box.setAlignment(Qt.AlignRight)
        h_box.addWidget(self.button_ok)
        h_box.addWidget(self.button_no)
        v_box.addWidget(self.question_label)
        v_box.addLayout(h_box)
        self.setLayout(v_box)

    def init_events(self):
        self.button_no.clicked.connect(self.on_button_no_clicked_handle)
        self.button_ok.clicked.connect(self.on_button_ok_clicked_handle)

    def on_button_no_clicked_handle(self):
        print("execute")
        self.close()

    def on_button_ok_clicked_handle(self):
        print("preview")
        self.close()

    pass
