# this code copied from https://ankiweb.net/shared/info/1423933177
from datetime import date, datetime
import time
from typing import Optional
from ..imports import common_tools
Anki = common_tools.compatible_import.Anki
if Anki.isQt6:
    from PyQt6 import QtGui
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import QAbstractButton, QWidget, QVBoxLayout, QShortcut, QGridLayout, QLabel
else:
    from PyQt5 import QtGui
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QAbstractButton, QWidget, QVBoxLayout, QShortcut, QGridLayout, QLabel
from anki.lang import _
from anki.stats import CardStats
import aqt
from aqt import qconnect, QPushButton, QHBoxLayout, QDialogButtonBox, QKeySequence, QCheckBox
# from aqt.previewer import Previewer
from anki.cards import Card
from aqt.browser.previewer import Previewer
from aqt.operations.scheduling import answer_card
from aqt.reviewer import V3CardInfo
from aqt.utils import tooltip, showInfo, tr
# from ..obj.utils import BaseInfo
# from ..obj import funcs, all_objs, clipper_imports
# this code copied from https://ankiweb.net/shared/info/1423933177
import unicodedata
import aqt

from anki.lang import _
from aqt import gui_hooks, QDialog, Qt, QDialogButtonBox, QKeySequence
from aqt.editor import Editor
from aqt.utils import saveGeom, restoreGeom
from aqt.webview import AnkiWebView
from anki.collection import Config
from typing import Union

from ..imports import common_tools
from ...common_tools import objs


class MyEditor(Editor):

    # no requireRest
    def onBridgeCmd(self, cmd):
        if not self.note:
            # shutdown
            return
        # focus lost or key/button pressed?
        if cmd.startswith("blur") or cmd.startswith("key"):
            (type, ord, nid, txt) = cmd.split(":", 3)
            ord = int(ord)
            try:
                nid = int(nid)
            except ValueError:
                nid = 0
            if nid != self.note.id:
                print("ignored late blur")
                return

            txt = unicodedata.normalize("NFC", txt)
            txt = self.mungeHTML(txt)
            # misbehaving apps may include a null byte in the text
            txt = txt.replace("\x00", "")
            # reverse the url quoting we added to get images to display
            txt = self.mw.col.media.escapeImages(txt, unescape=True)
            self.note.fields[ord] = txt
            if not self.addMode:
                self.note.flush()
                # self.mw.requireReset()
            if type == "blur":
                self.currentField = None
                # run any filters
                if gui_hooks.editor_did_unfocus_field(False, self.note, ord):
                    # something updated the note; update it after a subsequent focus
                    # event has had time to fire
                    self.mw.progress.timer(100, self.loadNoteKeepingFocus, False)
                else:
                    self.checkValid()
            else:
                gui_hooks.editor_did_fire_typing_timer(self.note)
                self.checkValid()
        # focused into field?
        elif cmd.startswith("focus"):
            (type, num) = cmd.split(":", 1)
            self.currentField = int(num)
            gui_hooks.editor_did_focus_field(self.note, self.currentField)
        elif cmd in self._links:
            self._links[cmd](self)
        else:
            print("uncaught cmd", cmd)


class EditNoteWindowFromThisLinkAddon(QDialog):

    def __init__(self, mw, note):
        QDialog.__init__(self, None, Qt.Window)
        mw.setupDialogGC(self)
        self.mw = mw
        self.form = aqt.forms.editcurrent.Ui_Dialog()
        self.form.setupUi(self)
        self.setWindowTitle(_("Anki: Edit underlying note (add-on window)"))
        self.setMinimumHeight(400)
        self.setMinimumWidth(250)
        self.form.buttonBox.button(QDialogButtonBox.Close).setShortcut(
            QKeySequence("Ctrl+Return"))
        self.editor = aqt.editor.Editor(self.mw, self.form.fieldsArea, self)
        self.editor.setNote(note, focusTo=0)
        restoreGeom(self, "note_edit")
        self.show()
        self.activateWindow()
        self.mw.progress.timer(100, lambda: self.editor.web.setFocus(), False)

    def reject(self):
        self.saveAndClose()

    def saveAndClose(self):
        self.editor.saveNow(self._saveAndClose)

    def _saveAndClose(self):
        saveGeom(self, "note_edit")
        QDialog.reject(self)

    def closeWithCallback(self, onsuccess):
        def callback():
            self._saveAndClose()
            onsuccess()

        self.editor.saveNow(callback)


def external_note_dialog(nid):
    d = EditNoteWindowFromThisLinkAddon(aqt.mw, nid)
    d.show()


# print, _1 = clipper_imports.funcs.logger(__name__)

class SingleCardPreviewer(Previewer):
    def __init__(self, card: Card, *args, **kwargs):
        self._card = card
        self._card.start_timer()
        self.ease_button: "dict[int,QPushButton]" = {}
        self.bottom_layout_rev = QGridLayout()
        self.bottom_layout_due = QGridLayout()
        self.bottom_tools_widget=QWidget()
        self.bottom_tools_widget_layout=QHBoxLayout()
        super().__init__(*args, **kwargs)
        mw = common_tools.compatible_import.mw

    def card(self) -> Card:
        return self._card

    def _create_gui(self):
        self.setWindowTitle(tr.actions_preview())
        self.close_shortcut = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        self.close_shortcut.activated.connect(self.close)
        qconnect(self.close_shortcut.activated, self.close)
        qconnect(self.finished, self._on_finished)
        self.silentlyClose = True
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self._web = AnkiWebView(title="previewer")
        self.vbox.addWidget(self._web)
        self.setLayout(self.vbox)
        restoreGeom(self, "preview")
        self.bottombar = QHBoxLayout()

        self._other_side = QPushButton("answer/review")
        self._other_side.setAutoDefault(False)
        self._other_side.clicked.connect(self._on_other_side)

        self.browser_button = QPushButton("show in browser")
        self.browser_button.clicked.connect(self._on_browser_button)
        self.browser_button.setText("show in browser")
        self.edit_button = QPushButton("edit")
        self.edit_button.clicked.connect(self._on_edit_button)

        self.answer_buttons = self._create_answer_buttons()
        self.answer_buttons.hide()

        self.due_info_widget = self._create_due_info_widget()
        self.inAdvance_button.setEnabled(False)

        self.bottom_tools_widget_layout.addWidget(self.browser_button)
        self.bottom_tools_widget_layout.addWidget(self.edit_button)
        self.bottom_tools_widget_layout.addWidget(self._other_side)
        self.bottom_tools_widget.setLayout(self.bottom_tools_widget_layout)
        self.bottom_layout_rev.addWidget(self.answer_buttons,0,0,1,1)
        self.bottom_layout_due.addWidget(self.due_info_widget,0,0,1,1)
        self.bottom_layout_due.addWidget(self.bottom_tools_widget,0,1,1,1)
        self.vbox.addLayout(self.bottom_layout_due)
        self.vbox.setStretch(0,1)
        self.vbox.setStretch(1,0)

    def should_review(self):
        today, next_date, last_date = self._fecth_date()
        return next_date <= today

    def _on_other_side(self):
        if self._state == "question":
            self._state = "answer"
            self._on_show_both_sides(True)
            self.inAdvance_button.setEnabled(True)
            if self.should_review():
                self.switch_to_answer_buttons()
            else:
                self.switch_to_due_info_widget()
        else:
            self.inAdvance_button.setEnabled(False)
            self.switch_to_due_info_widget()
            self._state = "question"
            self._show_both_sides = False
            self.render_card()

    def card_changed(self):


        return True


    def _on_browser_button(self):
        tooltip('browser clicked')
        browser = aqt.dialogs.open("Browser", self.mw)
        query = '"nid:' + str(self.card().nid) + '"'
        browser.form.searchEdit.lineEdit().setText(query)
        browser.onSearchActivated()

    def _on_edit_button(self):
        note = self.mw.col.getNote(self.card().nid)
        external_note_dialog(note)
        # aqt.QDialog.reject(self)
        # common_tools.funcs.PDFprev_close(self.card().id, all=True)

    def _create_answer_buttons(self):
        enum = ["","again","hard","good","easy"]
        widget = QWidget(self)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        sched = common_tools.compatible_import.mw.col.sched
        mw = common_tools.compatible_import.mw
        button_num = sched.answerButtons(self.card())
        for i in range(button_num):
            ease = enum[i+1]+":"+sched.nextIvlStr(self.card(),i+1)
            self.ease_button[i + 1] = QPushButton(ease)
            answer = lambda i: lambda :self._answerCard(i+1)
            self.ease_button[i+1].clicked.connect(answer(i))
            layout.addWidget(self.ease_button[i+1])
        widget.setLayout(layout)

        # common_tools.funcs.write_to_log_file(self.card().ivl.__str__())

        return widget

    def _update_answer_buttons(self):
        enum = ["", "again", "hard", "good", "easy"]
        sched = common_tools.compatible_import.mw.col.sched
        mw = common_tools.compatible_import.mw
        button_num = sched.answerButtons(self.card())
        for i in range(button_num):
            ease = enum[i + 1] + ":" + sched.nextIvlStr(self.card(), i + 1)
            self.ease_button[i + 1].setText(ease)

    def _answerCard(self,ease):
        say = common_tools.language.rosetta
        mw = common_tools.compatible_import.mw
        sched = common_tools.compatible_import.mw.col.sched
        signals = common_tools.G.signals
        answer = common_tools.configsModel.AnswerInfoInterface

        if self.card().timer_started is None:
            self.card().timer_started = time.time() - 60
        common_tools.funcs.CardOperation.answer_card(self.card(),ease)
        self.switch_to_due_info_widget()
        common_tools.funcs.LinkPoolOperation.both_refresh()
        mw.col.reset()
        common_tools.G.signals.on_card_answerd.emit(
            answer(platform=self, card_id=self.card().id, option_num=ease))


    def switch_to_answer_buttons(self):
        self._update_info()
        # self.bottom_layout_due.removeWidget(self.bottom_tools_widget)
        self.vbox.removeItem(self.bottom_layout_due)
        self.due_info_widget.hide()
        self.bottom_layout_rev.addWidget(self.bottom_tools_widget,0,1,1,1)
        self.vbox.addLayout(self.bottom_layout_rev)
        self.answer_buttons.show()
        cfg = common_tools.funcs.Config.get()
        if cfg.freeze_review.value:
            interval = cfg.freeze_review_interval.value
            self.freeze_answer_buttons()
            QTimer.singleShot(interval, lambda: self.recover_answer_buttons())

    def freeze_answer_buttons(self):
        for button in self.ease_button.values():
            button.setEnabled(False)
        tooltip(common_tools.funcs.Translate.已冻结)

    def recover_answer_buttons(self):
        for button in self.ease_button.values():
            button.setEnabled(True)
        tooltip(common_tools.funcs.Translate.已冻结)

    def switch_to_due_info_widget(self):
        self._update_info()
        self.answer_buttons.hide()
        self.vbox.removeItem(self.bottom_layout_rev)
        self.bottom_layout_due.addWidget(self.bottom_tools_widget,0,1,1,1)
        self.vbox.addLayout(self.bottom_layout_due)
        self.due_info_widget.show()

    def _update_info(self):
        self._update_answer_buttons()
        self._update_due_info_widget()

    def _update_due_info_widget(self):
        today, next_date, last_date = self._fecth_date()
        self.due_label.setText("可复习" if today>=next_date else "未到期")
        self.last_time_label.setText("上次复习:"+last_date.__str__())
        self.next_time_label.setText("下次复习:"+next_date.__str__())
        should_review = next_date<=today

    def _fecth_date(self):
        mw = common_tools.compatible_import.mw
        result = mw.col.db.execute(
            f"select id,ivl from revlog where id = (select  max(id) from revlog where cid = {self.card().id})"
        )
        if result:
            last,ivl = result[0]
            last_date = datetime.fromtimestamp(last / 1000)  # (Y,M,D,H,M,S,MS)

            common_tools.funcs.write_to_log_file(f"id={last},ivl={ivl}")
            if ivl>=0: #ivl 正表示天为单位,负表示秒为单位
                next_date = datetime.fromtimestamp(last / 1000 + ivl * 86400)  # (Y,M,D,H,M,S,MS)
            else:
                next_date = datetime.fromtimestamp(last/1000-ivl)
        else:
            ivl=0
            next_date = datetime.today()  # (Y,M,D,H,M,S,MS)
            last_date = datetime.today()  # (Y,M,D,H,M,S,MS)
        today = datetime.today()  # (Y,M,D,H,M,S,MS)

        return today,next_date,last_date


    def _create_due_info_widget(self):
        widget = QWidget(self)
        layout = QGridLayout(widget)
        widget.setContentsMargins(0,0,0,0)
        layout.setContentsMargins(0,0,0,0)
        today, next_date, last_date = self._fecth_date()
        self.inAdvance_button =QPushButton("提前学习")
        self.inAdvance_button.clicked.connect(self.switch_to_answer_buttons)
        self.due_label = QLabel("可复习" if next_date<=today else "可提前")
        self.last_time_label = QLabel("上次复习:"+last_date.__str__())
        self.next_time_label = QLabel("下次复习:"+next_date.__str__())
        layout.addWidget(self.due_label,0,0,2,1)
        layout.addWidget(self.last_time_label,0,1,1,1)
        layout.addWidget(self.next_time_label,1,1,1,1)
        layout.addWidget(self.inAdvance_button,0,2,2,1)
        widget.setLayout(layout)
        return widget

class SingleCardPreviewerMod(SingleCardPreviewer):

    def _on_bridge_cmd(self, cmd):
        super()._on_bridge_cmd(cmd)


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # common_tools.funcs.PDFprev_close(self.card().id, all=True)
        # addonName = BaseInfo().dialogName
        common_tools.G.mw_card_window[str(self.card().id)] = None
        # card_window = aqt.mw.__dict__[addonName]["card_window"]
        # card_window[str(self.card().id)]=None
        # print(all_objs.mw_card_window)


def unregister(card_id, *args, **kwargs):
    # addonName = common_tools.G.addonName
    # card_window = aqt.mw.__dict__[addonName]["card_window"]
    # card_window[card_id] = None
    common_tools.G.mw_card_window[card_id] = None


def external_card_dialog(card) -> 'Optional[SingleCardPreviewerMod]':
    """请自己做好卡片存在性检查,这一层不检查"""
    card_id = str(card.id)
    if card_id not in common_tools.G.mw_card_window:
        common_tools.G.mw_card_window[card_id] = None
    if common_tools.G.mw_card_window[card_id] is not None:
        common_tools.G.mw_card_window[card_id].activateWindow()
    else:
        d = SingleCardPreviewerMod(card=card, parent=aqt.mw, mw=aqt.mw, on_close=lambda: unregister(card_id))
        d.open()
        common_tools.G.mw_card_window[card_id] = d
    return common_tools.G.mw_card_window[card_id]