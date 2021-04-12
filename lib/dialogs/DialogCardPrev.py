# this code copied from https://ankiweb.net/shared/info/1423933177
import aqt
from anki.lang import _
from aqt import qconnect, QPushButton, QHBoxLayout, QDialogButtonBox, QKeySequence, QCheckBox
from aqt.previewer import Previewer
from anki.cards import Card
from aqt.utils import tooltip
from ..obj.utils import BaseInfo

from .DialogCardEditor import EditNoteWindowFromThisLinkAddon


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
        qconnect(self._other_side.clicked, self._on_other_side)

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
        self._show_both_sides = True
        self.both_sides_button.setChecked(self._show_both_sides)

    def _on_browser_button(self):
        tooltip('browser clicked')
        browser = aqt.dialogs.open("Browser", self.mw)
        query = '"nid:' + str(self.card().nid) + '"'
        browser.form.searchEdit.lineEdit().setText(query)
        browser.onSearchActivated()

    def _on_edit_button(self):
        note = self.mw.col.getNote(self.card().nid)
        d = EditNoteWindowFromThisLinkAddon(self.mw, note)
        d.show()
        aqt.QDialog.reject(self)

    def onShowRatingBar(self):
        pass


def unregister(id, *args, **kwargs):
    dialogName = BaseInfo().dialogName
    card_window = aqt.mw.__dict__[dialogName]["card_window"]
    card_window[id] = None


def external_card_dialog(card):
    dialogName = BaseInfo().dialogName
    card_window = aqt.mw.__dict__[dialogName]["card_window"]
    if card.id not in card_window:
        card_window[card.id] = None
    if card_window[card.id] is not None:
        card_window[card.id].activateWindow()
    else:
        d = SingleCardPreviewerMod(card=card, parent=aqt.mw, mw=aqt.mw, on_close=lambda: unregister(card.id))
        d.open()
        card_window[card.id] = d
