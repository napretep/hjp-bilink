# this code copied from https://ankiweb.net/shared/info/1423933177
from datetime import date, datetime
import time
from typing import Optional

from anki.notes import NoteId, Note

from ..imports import *

from anki.lang import _
from anki.stats import CardStats
# from aqt.previewer import Previewer
from anki.cards import Card

import unicodedata
from anki.lang import _
from anki.collection import Config
from anki.utils import point_version
from typing import Union

from ..imports import common_tools
from ...common_tools import objs

TR = common_tools.language.Translate

if not ISLOCAL:
    class MyEditor(Editor):

        # no requireRest
        def onBridgeCmd(self, cmd):
            if not self.note:
                # shutdown
                return

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


    class NewNoteEditorDialog(QMainWindow):
        """ for version 23.10+"""
        def __init__(self,superior, mw: aqt.AnkiQt,note:"Note") -> None:
            super().__init__(None, Qt.WindowType.Window)
            self.superior = superior
            self.mw = mw
            self.form = aqt.forms.editcurrent.Ui_Dialog()
            self.form.setupUi(self)
            self.setWindowTitle(tr.editing_edit_current())
            self.setMinimumHeight(400)
            self.setMinimumWidth(250)
            self.editor = aqt.editor.Editor(
                    self.mw,
                    self.form.fieldsArea,
                    self,
                    editor_mode=aqt.editor.EditorMode.EDIT_CURRENT,
            )
            self.editor.card = self.mw.col.get_card(note.card_ids()[0])
            self.editor.set_note(note, focusTo=0)
            restoreGeom(self, "editcurrent")
            close_button = self.form.buttonBox.button(QDialogButtonBox.StandardButton.Close)
            close_button.setShortcut(QKeySequence("Ctrl+Return"))
            # qt5.14+ doesn't handle numpad enter on Windows
            self.compat_add_shorcut = QShortcut(QKeySequence("Ctrl+Enter"), self)
            qconnect(self.compat_add_shorcut.activated, close_button.click)
            # gui_hooks.operation_did_execute.append(self.on_operation_did_execute)
            self.show()

        # def on_operation_did_execute(
        #         self, changes: OpChanges, handler: Optional[object]
        # ) -> None:
        #     if changes.note_text and handler is not self.editor:
        #         # reload note
        #         note = self.editor.note
        #         try:
        #             note.load()
        #         except NotFoundError:
        #             # note's been deleted
        #             self.cleanup()
        #             self.close()
        #             return
        #
        #         self.editor.set_note(note)

        def cleanup(self) -> None:
            # gui_hooks.operation_did_execute.remove(self.on_operation_did_execute)
            self.editor.cleanup()
            saveGeom(self, "editcurrent")
            # aqt.dialogs.markClosed("EditCurrent")

        def reopen(self, mw: aqt.AnkiQt) -> None:
            if card := self.mw.reviewer.card:
                self.editor.set_note(card.note())

        def closeEvent(self, evt: QCloseEvent) -> None:
            self.editor.call_after_note_saved(self.cleanup)

        def _saveAndClose(self) -> None:
            self.cleanup()
            self.mw.deferred_delete_and_garbage_collect(self)
            self.close()

        def closeWithCallback(self, onsuccess: Callable[[], None]) -> None:
            def callback() -> None:
                self._saveAndClose()
                onsuccess()

            self.editor.call_after_note_saved(callback)

        # onReset = on_operation_did_execute


    class NoteEditorDialog(QDialog):
        """
        TODO: note更新后要同步到对应的previewer
        this is for 2.1.66 ,not available in 23.10+
        """

        def __init__(self, superior, mw, note:"common_tools.compatible_import.Anki.notes.Note"):
            QDialog.__init__(self, None, Qt.WindowType.Window)
            mw.setupDialogGC(self)
            self.superior=superior
            self.mw = mw
            self.form = aqt.forms.editcurrent.Ui_Dialog()
            self.form.setupUi(self)
            self.setWindowTitle(f"editor of {note.card_ids()[0]}")
            self.setMinimumHeight(400)
            self.setMinimumWidth(250)
            self.form.buttonBox.button(QDialogButtonBox.Close).setShortcut(
                    QKeySequence("Ctrl+Return"))
            self.editor = aqt.editor.Editor(self.mw, self.form.fieldsArea, self)
            self.editor.setNote(note, focusTo=0)
            restoreGeom(self, "note_edit")
            # self.show()
            # self.activateWindow()
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


    # def external_note_dialog(nid):
    #     d = NoteEditorDialog(aqt.mw, nid)
    #     d.show()


    # print, _1 = clipper_imports.funcs.logger(__name__)

    class SingleCardPreviewer(Previewer):
        """这个东西的card必须不为空否则一些功能运行不了
        当你把它作为Qwidget打开时, 注意先运行open()

        """

        def __init__(self, card: Card=None, superior=None, *args, **kwargs):
            self._card = card
            self.editor: "Optional[NoteEditorDialog]" =None
            self.superior = superior
            if card:
                self.card().start_timer()
            self.bottom_layout_all = QGridLayout()
            self.bottom_tools_widget = QWidget()
            self.bottom_tools_widget_layout = QHBoxLayout()
            self.showBoth = QCheckBox(common_tools.language.Translate.双面展示)
            self.revWidget = common_tools.widgets.ReviewButtonForCardPreviewer(self, self.bottom_layout_all)
            super().__init__(*args, **kwargs)

            self.initEvent()
            self.handleBothSideEmit(common_tools.G.customPreviewerBothSide, init=True)

        def initEvent(self):
            common_tools.G.signals.onCardSwitchBothSide.connect(self.handleBothSideEmit)

        def activateAsSubWidget(self):
            self._state = "question"
            self._last_state = None
            self._create_gui()
            self._setup_web_view()
            self.render_card()

        def card(self) -> Card:
            # self._card.id.__str__()
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
            self._web = AnkiWebView(title=common_tools.baseClass.枚举命名.独立卡片预览器)
            self.vbox.addWidget(self._web)
            self.setLayout(self.vbox)
            restoreGeom(self, common_tools.baseClass.枚举命名.独立卡片预览器)
            self.bottombar = QHBoxLayout()

            self._other_side = QPushButton(QIcon(common_tools.G.src.ImgDir.right_direction), "")
            # self._other_side.setIcon()
            # self.browser_button = QPushButton("show in browser")
            self.edit_button = QPushButton(QIcon(common_tools.G.src.ImgDir.edit), "")

            self._other_side.setAutoDefault(False)
            self._other_side.clicked.connect(self._on_other_side)
            self.setWindowTitle(common_tools.baseClass.枚举命名.独立卡片预览器)
            # buttons
            # self.browser_button.clicked.connect(self._on_browser_button)
            # self.browser_button.setText("show in browser")

            self.edit_button.clicked.connect(self._on_edit_button)
            self.showBoth.clicked.connect(self.onShowBothClicked)
            # self.bottom_tools_widget_layout.addWidget(self.browser_button)
            self.bottom_tools_widget_layout.addWidget(self.showBoth)
            self.bottom_tools_widget_layout.addWidget(self.edit_button)
            self.bottom_tools_widget_layout.addWidget(self._other_side)
            self.bottom_tools_widget.setLayout(self.bottom_tools_widget_layout)
            self.bottom_layout_all.addWidget(self.bottom_tools_widget, 0, 1, 1, 1)
            self.vbox.addLayout(self.bottom_layout_all)
            self.vbox.setStretch(0, 1)
            self.vbox.setStretch(1, 0)

        def handleBothSideEmit(self, value, init=False):
            if value:
                self._state = "answer"
            else:
                self._state = "question"

            if init:
                self._show_both_sides = value
            else:
                self._on_show_both_sides(value)
            self.showBoth.blockSignals(True)
            self.showBoth.setChecked(value)
            self.showBoth.blockSignals(False)

        def onShowBothClicked(self):
            if self.showBoth.isChecked():
                self._state = "answer"
                self._on_show_both_sides(True)
                common_tools.G.customPreviewerBothSide = True
            else:
                self._state = "question"
                self._on_show_both_sides(False)
                common_tools.G.customPreviewerBothSide = False
            self.render_card()
            # 需要全局更新checkbox
            common_tools.G.signals.onCardSwitchBothSide.emit(self.showBoth.isChecked())

        def _on_other_side(self):
            if not self.showBoth.isChecked():
                if self._state == "question":
                    self._state = "answer"
                    self._on_show_both_sides(True)
                else:
                    self._state = "question"

                    self._on_show_both_sides(False)

            self.render_card()
            self.switchSideDirection()

        def switchSideDirection(self):
            if self._state == "question":
                self._other_side.setIcon(QIcon(common_tools.G.src.ImgDir.right_direction))
            else:
                self._other_side.setIcon(QIcon(common_tools.G.src.ImgDir.left_direction))

        def card_changed(self):
            return True

        def _on_browser_button(self):
            browser = aqt.dialogs.open("Browser", self.mw)
            query = '"nid:' + str(self.card().nid) + '"'
            browser.form.searchEdit.lineEdit().setText(query)
            browser.onSearchActivated()

        def _on_edit_button(self):
            note = self.mw.col.getNote(self.card().nid)
            if point_version()<=66:
                self.editor = NoteEditorDialog(self,aqt.mw, note)
            else:
                self.editor =NewNoteEditorDialog(self,aqt.mw, note)
            self.editor.show()
            # aqt.QDialog.reject(self)
            # common_tools.funcs.PDFprev_close(self.card().id, all=True)

        def _on_bridge_cmd(self, cmd):
            super()._on_bridge_cmd(cmd)

        def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
            # common_tools.funcs.PDFprev_close(self.card().id, all=True)
            # addonName = BaseInfo().dialogName
            common_tools.G.mw_card_window[str(self.card().id)] = None
            # common_tools.G.customPreviewerBothSide.disconnect(self.handleBothSideEmit)
            # card_window = aqt.mw.__dict__[addonName]["card_window"]
            # card_window[str(self.card().id)]=None
            # print(all_objs.mw_card_window)

        def loadNewCard(self, card):
            self._card = card
            self.render_card()
            self.revWidget.update_info()
            self.handleBothSideEmit(common_tools.G.customPreviewerBothSide, init=True)
            self.switchSideDirection()


    #
    # class SingleCardPreviewerMod(SingleCardPreviewer):
    #

    def unregister(card_id, *args, **kwargs):
        # addonName = common_tools.G.addonName
        # card_window = aqt.mw.__dict__[addonName]["card_window"]
        # card_window[card_id] = None
        common_tools.G.mw_card_window[card_id] = None


    def external_card_dialog(card) -> 'Optional[SingleCardPreviewer]':
        """请自己做好卡片存在性检查,这一层不检查"""
        card_id = str(card.id)
        if card_id not in common_tools.G.mw_card_window:
            common_tools.G.mw_card_window[card_id] = None
        if common_tools.G.mw_card_window[card_id] is not None:
            common_tools.G.mw_card_window[card_id].activateWindow()
        else:
            d = SingleCardPreviewer(card=card, parent=aqt.mw, mw=aqt.mw, on_close=lambda: unregister(card_id))
            d.open()
            common_tools.G.mw_card_window[card_id] = d
        return common_tools.G.mw_card_window[card_id]
