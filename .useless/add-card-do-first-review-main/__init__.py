import aqt
from aqt import gui_hooks, mw
from aqt.utils import tooltip
from aqt.qt import *
from aqt.editor import Editor
import time
from functools import lru_cache

pressed_add_card_and_review = False


# config stuff
def _get_cache_key():
    return round(time.time() / 2)

@lru_cache()
def _get_config(cache_key):
    return mw.addonManager.getConfig(__name__)

def get_config(key):
    config = _get_config(_get_cache_key())
    try:
        return config[key]
    except (KeyError, TypeError):
        return None


# addon stuff
def extend_add_cards(add_cards):
    global pressed_add_card_and_review

    button_box = add_cards.form.buttonBox
    sc = get_config("shortcut")

    def add_and_review():
        global pressed_add_card_and_review

        pressed_add_card_and_review = True
        add_cards.addCards()

    add_and_review_button = QPushButton("Add+Review")
    qconnect(add_and_review_button.clicked, add_and_review)
    add_and_review_button.setShortcut(QKeySequence(sc))
    add_and_review_button.setToolTip(f"Add and do first review.<br>Shortcut:{sc}")

    button_box.addButton(add_and_review_button, QDialogButtonBox.ActionRole)

    add_cards.update()

def added_note(note):
    global pressed_add_card_and_review
    global _timer

    if pressed_add_card_and_review is False:
        return

    i = 0
    for card in note.cards():
        i += 1
        card.timerStarted = time.time() - get_config("time")
        if mw.col.schedVer() == 2:
            ease = 3
        else:
            ease = 2
        mw.col.sched.answerCard(card, ease)

    def showTooltip():
        tooltip(f"""...and reviewed {i} card(s)!""", period=1000)

    # dirty workaround for showing the add-on tooltip after the the "Added" tooltip
    if get_config("show_tooltip"):
        _timer = QTimer()
        _timer.setSingleShot(True)
        _timer.timeout.connect(showTooltip)
        _timer.start(500)

    pressed_add_card_and_review = False

gui_hooks.add_cards_did_init.append(extend_add_cards)
gui_hooks.add_cards_did_add_note.append(added_note)
