from .linkTool import *

#以下代码借鉴自插件 1423933177





if pointVersion() <= 28:
    from aqt.previewer import SingleCardPreviewer
else:
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
            else:
                self._state = "question"
            self.render_card()

        def card_changed(self):
            return True
