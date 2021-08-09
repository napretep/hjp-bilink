# this code copied from https://ankiweb.net/shared/info/1423933177
import unicodedata

import aqt

from anki.lang import _
from aqt import gui_hooks, QDialog, Qt, QDialogButtonBox, QKeySequence
from aqt.editor import Editor
from aqt.utils import saveGeom, restoreGeom


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
