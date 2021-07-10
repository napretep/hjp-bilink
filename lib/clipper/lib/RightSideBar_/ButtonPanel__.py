import json

from PyQt5 import QtGui
from PyQt5.QtGui import QTextFormat, QIcon
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QToolButton, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar, \
    QGridLayout
from PyQt5.QtCore import Qt

from ..tools import events, funcs, objs, ALL
print, printer = funcs.logger(__name__)

class CardinfosPreviewer(QDialog):
    pass


class ClipperExecuteProgresser(QDialog):
    def __init__(self, rightsidebar=None):
        super().__init__(parent=rightsidebar)
        self.rightsidebar = rightsidebar
        self.prepare_progress = objs.ProgressBarBlackFont(self)
        self.init_UI()
        # self.init_events()
        self.__event = {
            ALL.signals.on_ClipperExecuteProgresser_show: self.on_ClipperExecuteProgresser_show_handle,
        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()

    def init_job(self):
        from .. import RightSideBar_
        self.job = RightSideBar_.FinalExecution_masterJob(cardlist=self.rightsidebar.cardlist)
        self.job.on_job_progress.connect(self.progress_dispatcher)
        self.job.on_job_done.connect(self.on_masterjob_done_handle)
        self.job.start()

    def on_masterjob_done_handle(self, timestamp):
        # self.setWindowModality(Qt.NonModal)
        self.close()
        # print(f"on_masterjob_done_handle timestamp={timestamp}")
        e = events.AnkiBrowserActivateEvent
        ALL.signals.on_anki_browser_activate.emit(
            e(eventType=e.ClipperTaskFinishedType, sender=self, data=timestamp)
        )
        self.prepare_progress.setFormat("任务完成/task complete %p%")
        ALL.clipper.close()

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
        g_layout = QGridLayout(self)

        g_layout.addWidget(self.prepare_progress, 0, 0, 1, 4)
        self.setLayout(g_layout)

    #
    # def init_events(self):
    #
    #     # self.setShortcutEnabled()
    #     pass

    def on_ClipperExecuteProgresser_show_handle(self):
        self.init_job()

    pass


class CardinfosPreviewConfirm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.button_ok = QToolButton(self)
        self.button_no = QToolButton(self)
        self.question_label = QLabel(self)
        self.init_UI()
        self.__event = {
            self.button_no.clicked: self.on_button_no_clicked_handle,
            self.button_ok: self.on_button_ok_clicked_handle
        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()

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

    # def init_events(self):
    #     self.button_no.clicked.connect(self.on_button_no_clicked_handle)
    #     self.button_ok.clicked.connect(self.on_button_ok_clicked_handle)

    def on_button_no_clicked_handle(self):
        print("execute")
        self.close()

    def on_button_ok_clicked_handle(self):
        print("preview")
        self.close()

    pass
