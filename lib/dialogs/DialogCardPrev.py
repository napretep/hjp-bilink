# this code copied from https://ankiweb.net/shared/info/1423933177
import aqt
from PyQt5 import QtGui
from anki.lang import _
from aqt import qconnect, QPushButton, QHBoxLayout, QDialogButtonBox, QKeySequence, QCheckBox
from aqt.previewer import Previewer
from anki.cards import Card
from aqt.utils import tooltip
from ..obj.utils import BaseInfo
from ..obj import funcs, all_objs, clipper_imports
from .DialogCardEditor import EditNoteWindowFromThisLinkAddon, external_note_dialog

print, _1 = clipper_imports.funcs.logger(__name__)

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

        self.showRate = QPushButton("G")  # grade - "R" is already used for replay audio
        self.showRate.setFixedWidth(25)
        self.showRate.clicked.connect(self.onShowRatingBar)

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
        funcs.PDFprev_close(self.card().id, all=True)

    def onShowRatingBar(self):
        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        funcs.PDFprev_close(self.card().id, all=True)
        # addonName = BaseInfo().dialogName
        all_objs.mw_card_window[str(self.card().id)] = None
        # card_window = aqt.mw.__dict__[addonName]["card_window"]
        # card_window[str(self.card().id)]=None
        # print(all_objs.mw_card_window)

def unregister(card_id, *args, **kwargs):
    addonName = BaseInfo().dialogName
    card_window = aqt.mw.__dict__[addonName]["card_window"]
    card_window[card_id] = None


def external_card_dialog(card):
    # addonName = BaseInfo().dialogName
    # card_window = aqt.mw.__dict__[addonName]["card_window"]
    card_window = all_objs.mw_card_window
    card_id = str(card.id)
    if card_id not in card_window:
        card_window[card_id] = None
    # print(card_window == all_objs.mw_card_window)
    if card_window[card_id] is not None:
        card_window[card_id].activateWindow()
    else:
        d = SingleCardPreviewerMod(card=card, parent=aqt.mw, mw=aqt.mw, on_close=lambda: unregister(card_id))
        d.open()
        card_window[card_id] = d
