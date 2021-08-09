# this code copied from https://ankiweb.net/shared/info/1423933177
import aqt
from PyQt5 import QtGui
from anki.lang import _
from aqt import qconnect, QPushButton, QHBoxLayout, QDialogButtonBox, QKeySequence, QCheckBox
# from aqt.previewer import Previewer
from anki.cards import Card
from aqt.browser.previewer import Previewer
from aqt.utils import tooltip, showInfo
# from ..obj.utils import BaseInfo
# from ..obj import funcs, all_objs, clipper_imports
# this code copied from https://ankiweb.net/shared/info/1423933177
import unicodedata
import aqt

from anki.lang import _
from aqt import gui_hooks, QDialog, Qt, QDialogButtonBox, QKeySequence
from aqt.editor import Editor
from aqt.utils import saveGeom, restoreGeom

from ..imports import common_tools


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
        super().__init__(*args, **kwargs)

    def card(self) -> Card:
        return self._card

    def _create_gui(self):
        super()._create_gui()
        self._other_side = self.bbox.addButton(
            "Other side", QDialogButtonBox.ActionRole
        )
        self._other_side.setAutoDefault(False)
        self._other_side.setShortcut(QKeySequence("Right"))
        self._other_side.setShortcut(QKeySequence("Left"))
        self._other_side.setToolTip(_("Shortcut key: Left or Right arrow"))
        # qconnect(self._other_side.is_selected, self._on_other_side)
        self._other_side.clicked.connect(self._on_other_side)

    def _on_other_side(self):
        if self._state == "question":
            self._state = "answer"
            self._on_show_both_sides(True)
        else:
            self._state = "question"
            self._show_both_sides = False
            self.render_card()

    def card_changed(self):
        return True


class SingleCardPreviewerMod(SingleCardPreviewer):

    def _on_bridge_cmd(self, cmd):
        super()._on_bridge_cmd(cmd)

    def _create_gui(self):
        super()._create_gui()

        self.vbox.removeWidget(self.bbox)
        self.bottombar = QHBoxLayout()

        self.browser_button = QPushButton("show in browser")
        self.browser_button.clicked.connect(self._on_browser_button)
        self.bottombar.addWidget(self.browser_button)

        self.edit_button = self.bbox.addButton("edit", QDialogButtonBox.HelpRole)
        self.edit_button.clicked.connect(self._on_edit_button)
        self.bottombar.addWidget(self.edit_button)

        # self.showRate = QPushButton("G")  # grade - "R" is already used for replay audio
        # self.showRate.setFixedWidth(25)
        # self.showRate.clicked.connect(self.onShowRatingBar)

        self.bottombar.addWidget(self.bbox)
        self.vbox.addLayout(self.bottombar)

    def _setup_web_view(self):
        super()._setup_web_view()
        for child in self.bbox.children():
            if isinstance(child, QCheckBox):
                self.both_sides_button = child
        self._show_both_sides = False
        self.both_sides_button.setChecked(self._show_both_sides)

    def _on_browser_button(self):
        tooltip('browser clicked')
        browser = aqt.dialogs.open("Browser", self.mw)
        query = '"nid:' + str(self.card().nid) + '"'
        browser.form.searchEdit.lineEdit().setText(query)
        browser.onSearchActivated()

    def _on_edit_button(self):
        note = self.mw.col.getNote(self.card().nid)
        external_note_dialog(note)
        aqt.QDialog.reject(self)
        common_tools.funcs.PDFprev_close(self.card().id, all=True)

    def onShowRatingBar(self):
        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        common_tools.funcs.PDFprev_close(self.card().id, all=True)
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


def external_card_dialog(card):
    card_id = str(card.id)

    if len(aqt.mw.col.find_cards(f"cid:{card_id}")) == 0:
        showInfo(f"{card_id} 卡片不存在/card don't exist")
        return
    if card_id not in common_tools.G.mw_card_window:
        common_tools.G.mw_card_window[card_id] = None
    if common_tools.G.mw_card_window[card_id] is not None:
        common_tools.G.mw_card_window[card_id].activateWindow()
    else:
        d = SingleCardPreviewerMod(card=card, parent=aqt.mw, mw=aqt.mw, on_close=lambda: unregister(card_id))
        d.open()
        common_tools.G.mw_card_window[card_id] = d
