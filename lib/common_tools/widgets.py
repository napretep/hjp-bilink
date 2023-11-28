# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'mywidgets.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/1 16:48'
"""
import abc
import math
import os
import re
import urllib

from .compatible_import import *
from .language import Translate, rosetta
from . import configsModel

from . import funcs, baseClass, hookers, funcs2
from .all_widgets.basic_widgets import *
from .all_widgets.prop_widgets import *
from .all_widgets.selector_widgets import *
from .all_widgets.config_widgets import *
from .all_widgets.widget_funcs import *

布局 = 框 = 0
组件 = 件 = 1
子代 = 子 = 2
占 = 占据 = 3
# from ..bilink.dialogs.linkdata_grapher import Grapher

if __name__ == "__main__":
    from lib.common_tools import G
else:
    from . import G

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .configsModel import *

译 = Translate


class SafeImport:
    @property
    def models(self):
        from . import models
        return models


safe = SafeImport()


class GridHDescUnit(QWidget):
    def __init__(self, parent=None, labelname=None, tooltip=None, widget=None):
        super().__init__(parent)
        self.label = QLabel(self)
        self.label.setText(labelname)
        self.label.setToolTip(tooltip)
        self.widget = widget
        self.H_layout = QGridLayout(self)
        self.H_layout.addWidget(self.label, 0, 0)
        self.H_layout.addWidget(self.widget, 0, 1)
        self.H_layout.setSpacing(0)
        self.setLayout(self.H_layout)
        self.widget.setParent(self)
        self.setContentsMargins(0, 0, 0, 0)

    def setDescText(self, txt):
        self.label.setText(txt)

    def setDescTooltip(self, txt):
        self.label.setToolTip(txt)


class ProgressBarBlackFont(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("text-align:center;color:black;")

    pass


class UniversalProgresser(QDialog):
    on_close = pyqtSignal()  #

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.progressbar = ProgressBarBlackFont(self)
        self.intro = QLabel("if crashed, press esc to quit", self)
        self.signal_func_dict: "Optional[dict[str,list[callable,callable,Union[dict,None]]]]" = None  # "signal_name":[signal,funcs,kwargs] 传入的信号与槽函数
        self.signal_sequence: "Optional[list[list[str]]]" = None  # [["signal_name"]] 0,1,2 分别是前,中,后的回调函数.
        self.timer = QTimer()
        self.format_dict = {}
        self.event_dict = {}
        self.init_UI()
        self.show()

    def close_dely(self, dely=100):
        self.timer.singleShot(dely, self.close)

    def data_load(self, format_dict=None, signal_func_dict=None, signal_sequence=None):
        from . import objs
        if self.signal_sequence is not None:
            raise ValueError("请先启动data_clear,再赋值")
        self.format_dict = format_dict
        self.signal_sequence = signal_sequence
        self.signal_func_dict = signal_func_dict
        if self.signal_sequence is not None:
            if len(self.signal_sequence) != 3:
                raise ValueError("signal_sequence 的元素必须是 3个数组")
        if self.signal_func_dict is not None:
            self.event_dict = {}
            for k, v in self.signal_func_dict.items():
                if len(v) != 3:
                    raise ValueError("signal_func_dict 的value必须是长度为3的数组")
                self.event_dict[v[0]] = v[1]
                if v[2] is not None:
                    v[2]["type"] = self.__class__.__name__
            self.all_event = objs.AllEventAdmin(self.event_dict).bind()
        return self

    def data_clear(self):
        self.signal_func_dict = None  # "signal_name":[signal,func] 传入的信号与槽函数
        self.signal_sequence = None  # ["signal_name",{"args":[],"kwargs":{}]
        self.pdf_page_list = None  # [[pdfdir,pagenum]]
        self.all_event.unbind()
        return self

    def valtxt_set(self, value, format=None):
        """set value and format,"""
        if format is not None:
            self.progressbar.setFormat(format)
        self.progressbar.setValue(value)

    def value_set(self, event: "Progress"):
        if type(event) != int:  # 有些地方直接插入数字了
            self.progressbar.setValue(event.value)
            if event.text is not None:
                self.progressbar.setFormat(event.text)
        else:
            self.progressbar.setValue(event)

    def init_UI(self):
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        glayout = QGridLayout(self)
        glayout.addWidget(self.progressbar, 0, 0, 1, 4)
        glayout.addWidget(self.intro, 1, 0, 1, 1)
        self.setLayout(glayout)


class SupportDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(G.src.ImgDir.heart))
        self.setWindowTitle("支持作者/support author")
        self.alipayPic = QPixmap(G.src.ImgDir.qrcode_alipay)
        self.alipaylabel = QLabel(self)
        self.alipaylabel.setPixmap(self.alipayPic)
        self.alipaylabel.setScaledContents(True)
        self.alipaylabel.setMaximumSize(300, 300)
        self.weixinpaylabel = QLabel(self)
        self.weixinpaylabel.setPixmap(QPixmap(G.src.ImgDir.qrcode_weixinpay))
        self.weixinpaylabel.setScaledContents(True)
        self.weixinpaylabel.setMaximumSize(300, 300)
        self.desclabel = QLabel(self)
        self.desclabel.setText("点赞、转发、分享给更多人，也是一种支持！")
        self.desclabel.setAlignment(Qt.AlignCenter)
        self.v_layout = QVBoxLayout(self)
        self.h_layout = QHBoxLayout(self)
        self.h_layout.addWidget(self.weixinpaylabel)
        self.h_layout.setStretch(0, 1)
        self.h_layout.setStretch(1, 1)
        self.h_layout.addWidget(self.alipaylabel)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.desclabel)
        self.setMaximumSize(400, 400)
        self.setLayout(self.v_layout)
        self.show()



class Dialog_PDFUrlTool(QDialog):

    def __init__(self):
        super().__init__()
        self.resize(500, 200)
        self.class_name = G.src.pdfurl_class_name
        layout = QFormLayout(self)
        self.setWindowTitle("PDFUrlTool")
        self.widgets:Dict[str,Union[QTextEdit,QSpinBox,QRadioButton,QToolButton]] = {
                Translate.pdf路径    : QTextEdit(self),
                Translate.pdf页码    : QSpinBox(self),
                Translate.pdf名字    : QTextEdit(self),
                Translate.pdf默认显示页码: QRadioButton(self),
                Translate.pdf样式    : QTextEdit(self),
                Translate.确定       : QToolButton(self)
        }
        self.widgets[Translate.pdf页码].setRange(0, 99999)
        list(map(lambda items: layout.addRow(items[0], items[1]), self.widgets.items()))
        self.needpaste = False
        self.widgets[Translate.pdf路径].textChanged.connect(lambda: self.on_pdfpath_changed(self.widgets[Translate.pdf路径].toPlainText()))

        self.widgets[Translate.确定].clicked.connect(lambda event: self.on_confirm_clicked())
        self.widgets[Translate.确定].setIcon(QIcon(G.src.ImgDir.correct))
        QShortcut(QKeySequence(Qt.Key_Enter), self).activated.connect(lambda: self.widgets[Translate.确定].click())
        self.widgets[Translate.pdf路径].setAcceptRichText(False)
        # self.widgets[Translate.确定].clicked.connect()

    def on_pdfpath_changed(self, path):
        text = re.sub("^file:/{2,3}", "", urllib.parse.unquote(path))
        splitresult = re.split("#page=(\d+)$", text)
        if len(splitresult) > 1:
            self.widgets[Translate.pdf页码].setValue(int(splitresult[1]))
        pdffilepath = splitresult[0]
        config: "list" = funcs.PDFLink.GetPathInfoFromPreset(pdffilepath)
        if config is not None:
            pdffilename = config[1]
        else:
            pdffilename = os.path.splitext(os.path.basename(pdffilepath))[0]
        # pdffilename, _ = config[1] if config is not None else os.path.splitext(os.path.basename(pdffilepath))
        self.widgets[Translate.pdf路径].blockSignals(True)
        self.widgets[Translate.pdf路径].setText(pdffilepath)
        self.widgets[Translate.pdf路径].blockSignals(False)
        self.widgets[Translate.pdf名字].setText(pdffilename)

    def get_url_name_num(self) -> Tuple[str, str, str]:
        return self.widgets[Translate.pdf路径].toPlainText(), \
               self.widgets[Translate.pdf名字].toPlainText(), \
               self.widgets[Translate.pdf页码].value()

    def on_confirm_clicked(self):
        self.needpaste = True
        clipboard = QApplication.clipboard()
        mmdata = QMimeData()
        pdfurl, pdfname, pdfpage = self.get_url_name_num()
        quote = re.sub(r"\\", "/", pdfurl)
        page_str = self.get_pdf_str(pdfpage) if self.widgets[Translate.pdf默认显示页码].isChecked() else ""
        style = self.widgets[Translate.pdf样式].toPlainText()
        bs = BeautifulSoup("", "html.parser")
        a_tag = bs.new_tag("a", attrs={
                "class": self.class_name,
                "style": style,
                "href" : f"file://{quote}#page={pdfpage}"
        })
        a_tag.string = pdfname + page_str
        mmdata.setHtml(a_tag.__str__())
        mmdata.setText(pdfurl)
        clipboard.setMimeData(mmdata)
        self.close()

    def get_pdf_str(self, page):
        from . import funcs, terms
        s = funcs.Config.get().PDFLink_pagenum_str.value
        return re.sub(f"{{{terms.PDFLink.page}}}", f"{page}", s)


def message_box_for_time_up(seconds):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(f"{seconds} {rosetta('秒')} {rosetta('时间到')},{rosetta('请选择后续操作')}:")
    msgBox.setWindowTitle("time up")
    msgBox.addButton(Translate.取消, QMessageBox.ButtonRole.NoRole)
    msgBox.addButton(Translate.重新计时, QMessageBox.ButtonRole.ResetRole)
    msgBox.addButton(Translate.默认操作, QMessageBox.ButtonRole.AcceptRole)
    msgBox.exec_()
    return msgBox.clickedButton().text()





class ReviewButtonForCardPreviewer:
    def __init__(self, papa, layout: "QGridLayout"):
        from . import hookers
        from ..bilink.dialogs.custom_cardwindow import SingleCardPreviewer
        self.papa: "SingleCardPreviewer" = papa
        self.ease_button: "dict[int,QPushButton]" = {}
        self.review_buttons = self._create_review_buttons()
        self.due_info = self._create_due_info_widget()
        self.当完成复习 = hookers.当_ReviewButtonForCardPreviewer_完成复习()
        layout.addWidget(self.due_info, 0, 0, 1, 1)
        self.initEvent()

    def initEvent(self):
        G.signals.on_card_answerd.connect(self.handle_on_card_answerd)

        pass

    def handle_on_card_answerd(self, answer: "configsModel.AnswerInfoInterface"):
        # from ..bilink.dialogs.linkdata_grapher import GrapherRoamingPreviewer
        #
        # notself, equalId, isRoaming = answer.platform != self, answer.card_id == self.card().id, isinstance(self.papa.superior, GrapherRoamingPreviewer)
        # # print(f"handle_on_card_answerd,{notself},{equalId},{isRoaming}")
        # if notself and equalId and isRoaming:
        #     # print("handle_on_card_answerd>if>ok")
        #     self.papa.superior.nextCard()
        pass

    def card(self):
        return self.papa.card()

    def _create_review_buttons(self):
        enum = ["", "again", "hard", "good", "easy"]
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        sched = mw.col.sched

        button_num = sched.answerButtons(self.card())
        for i in range(button_num):
            ease = enum[i + 1] + ":" + sched.nextIvlStr(self.card(), i + 1)
            self.ease_button[i + 1] = QPushButton(ease)
            answer = lambda j: lambda: self._answerCard(j + 1)
            self.ease_button[i + 1].clicked.connect(answer(i))
            layout.addWidget(self.ease_button[i + 1])
        widget.setLayout(layout)
        return widget

    def _create_due_info_widget(self):
        """due info 包括
        1 label显示复习状态
        2 button点击开始复习(button根据到期情况,显示不同的提示文字)
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        widget.setContentsMargins(0, 0, 0, 0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.due_label = QLabel()
        self._setDueInfo()
        layout.addWidget(self.due_label)
        layout.addWidget(self.review_buttons)
        widget.setLayout(layout)
        return widget

    def _setDueInfo(self):
        now = datetime.datetime.now()
        lastDate, nextDate = self.realDue()
        due = now >= nextDate
        self.due_label.setText((f"{Translate.可复习}" if due else f"{Translate.未到期}") + f"\n{nextDate}"[:-10])
        self.due_label.setStyleSheet("background-color:" + ("red" if due else "green") + f";color:white")

    def realDue(self):
        # 由于card.due落后,所以直接从数据库去取
        """由于 card.due受各种因素影响, 因此 他不能被正确地记录, 因此我需要用别的东西来替代."""

        return funcs.CardOperation.getLastNextRev(self.card().id)

    def _answerCard(self, ease):
        say = rosetta

        sched = mw.col.sched
        signals = G.signals
        answer = configsModel.AnswerInfoInterface

        if self.card().timer_started is None:
            self.card().timer_started = time.time() - 60
        funcs.CardOperation.answer_card(self.card(), ease)
        # self.switch_to_due_info_widget()
        funcs.LinkPoolOperation.both_refresh()
        mw.col.reset()
        G.signals.on_card_answerd.emit(
                answer(platform=self, card_id=self.card().id, option_num=ease))
        self.update_info()
        self.当完成复习(self.card().id, ease, self.papa)

    def update_info(self):
        self._update_answer_buttons()
        self._update_due_info_widget()

    def _update_answer_buttons(self):
        enum = ["", "again", "hard", "good", "easy"]
        sched = mw.col.sched
        button_num = sched.answerButtons(self.card())
        for i in range(button_num):
            ease = enum[i + 1] + ":" + sched.nextIvlStr(self.card(), i + 1)
            self.ease_button[i + 1].setText(ease)

    def _update_due_info_widget(self):
        self._setDueInfo()

    def ifNeedFreeze(self):
        cfg = funcs.Config.get()
        if cfg.freeze_review.value:
            interval = cfg.freeze_review_interval.value
            self.freeze_answer_buttons()
            QTimer.singleShot(interval, lambda: self.recover_answer_buttons())

    def freeze_answer_buttons(self):
        for button in self.ease_button.values():
            button.setEnabled(False)
        tooltip(Translate.已冻结)

    def recover_answer_buttons(self):
        for button in self.ease_button.values():
            button.setEnabled(True)
        tooltip(Translate.已解冻)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # f = tag_chooser_for_cards()
    # f.show()
    sys.exit(app.exec_())
