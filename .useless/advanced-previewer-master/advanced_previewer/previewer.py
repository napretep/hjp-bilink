# -*- coding: utf-8 -*-

"""
This file is part of the Advanced Previewer add-on for Anki

General previewer user interface

Copyright: Glutanimate 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import re
import time

from aqt.qt import *
from aqt.browser import Browser
from aqt.webview import AnkiWebView
from aqt.utils import (getBase, mungeQA, openLink,
                       saveGeom, restoreGeom, tooltip, askUser)

from anki.lang import _
from anki.consts import *

from anki.hooks import wrap, runFilter
from anki.sound import clearAudioQueue, playFromText, play
from anki.js import browserSel
from anki.utils import json

from .html import *
from .config import loadConfig
from .utils import trySetAttribute, transl

# Shortcuts for each ease button
PRIMARY_KEYS = (Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4)  # 1,2,3,4
SECONDARY_KEYS = (Qt.Key_J, Qt.Key_K, Qt.Key_L, Qt.Key_Odiaeresis)  # J,K,L,Ö

# support for JS Booster add-on
try:
    from jsbooster.location_hack import getBaseUrlText, stdHtmlWithBaseUrl

    preview_jsbooster = True
except ImportError:
    preview_jsbooster = False


class Previewer(QDialog):
    """Advanced Previewer window"""

    def __init__(self, browser):
        super(Previewer, self).__init__(parent=browser)
        self.b = browser
        self.mw = self.b.mw
        # list of currently previewed card ids
        self.cards = []
        self.card = self.b.card
        # indicates whether user clicked on card in preview
        self.linkClicked = False
        self.setWindowTitle(_("Preview"))
        self.setObjectName("Previewer")
        self.setupConfig()
        self.initUI()
        self.finished.connect(self.b._onPreviewFinished)

    def setupConfig(self):
        # Initialize a number of variables used by the add-on:
        self.config = loadConfig()
        self.multi = False
        self.state = "question"
        self.revAhead = False
        self.revAnswers = []
        self._revTimer = 0
        self.both = self.config["dsp"][0]
        if self.both:
            self.state = "answer"
        self.b._previewState = self.state

    def initUI(self):
        self.web = self.initWeb()
        self.b._previewWeb = self.web
        layout = self.setupMainLayout()
        self.setLayout(layout)
        self.setupHotkeys()
        restoreGeom(self, "preview")

    def setupMainLayout(self):
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        # Set up buttons:
        bottom = QWidget()
        bottom_l = QHBoxLayout()
        bottom_l.setContentsMargins(0, 0, 0, 5)
        bottom.setLayout(bottom_l)
        bottom.setMaximumHeight(80)
        left = QHBoxLayout()
        right = QHBoxLayout()
        left.setAlignment(Qt.AlignBottom)
        right.setAlignment(Qt.AlignBottom)
        left.setContentsMargins(0, 0, 0, 0)
        right.setContentsMargins(0, 0, 0, 0)

        # 1: answer buttons
        if self.config["rev"][0]:  # reviewing enabled?
            self.revArea = self.setupReviewArea()
            left.addWidget(self.revArea)
            self.revArea.hide()

        # 2: other buttons
        bbox = QDialogButtonBox()
        self.btnSides = bbox.addButton(
            transl("Both sides"), QDialogButtonBox.ActionRole)
        self.btnSides.setAutoDefault(False)
        self.btnSides.setShortcut(QKeySequence("B"))
        self.btnSides.setToolTip(_("Shortcut key: %s" % "B"))
        self.btnSides.setCheckable(True)
        self.btnSides.setChecked(self.both)
        btnReplay = bbox.addButton(
            _("Replay Audio"), QDialogButtonBox.ActionRole)
        btnReplay.setAutoDefault(False)
        btnReplay.setShortcut(QKeySequence("R"))
        btnReplay.setToolTip(_("Shortcut key: %s" % "R"))
        self.btnPrev = bbox.addButton("<", QDialogButtonBox.ActionRole)
        self.btnPrev.setAutoDefault(False)
        self.btnPrev.setShortcut(QKeySequence("Left"))
        self.btnPrev.setToolTip(_("Shortcut key: Right arrow"))
        self.btnNext = bbox.addButton(">", QDialogButtonBox.ActionRole)
        self.btnNext.setToolTip(_("Shortcut key: Right arrow or Enter"))
        self.btnNext.setAutoDefault(True)
        self.btnNext.setShortcut(QKeySequence("Right"))

        self.btnSides.clicked.connect(self.onSidesToggle)
        self.btnPrev.clicked.connect(self.onPrev)
        self.btnNext.clicked.connect(self.onNext)
        btnReplay.clicked.connect(self.b._onReplayAudio)

        right.addWidget(bbox)
        bottom_l.addLayout(left)
        bottom_l.addLayout(right)

        vbox.addWidget(self.web, 10)
        # Set up window and launch preview
        vbox.addWidget(bottom, 0)

        return vbox

    def setupHotkeys(self):
        QShortcut(QKeySequence(_("Ctrl+Z")),
                  self, activated=self.mw.onUndo)
        QShortcut(QKeySequence(_("Ctrl+J")),
                  self, activated=self.b.onSuspend)
        QShortcut(QKeySequence(_("Ctrl+K")),
                  self, activated=self.b.onMark)
        QShortcut(QKeySequence(_("Alt+Delete")),
                  self, activated=self.b.deleteNotes)
        QShortcut(QKeySequence(_("Alt+Home")),
                  self, activated=lambda: self.onMove("s"))
        QShortcut(QKeySequence(_("Alt+End")),
                  self, activated=lambda: self.onMove("e"))
        QShortcut(QKeySequence(_("Alt+PgDown")),
                  self, activated=lambda: self.onMove("n"))
        QShortcut(QKeySequence(_("Alt+PgUp")),
                  self, activated=lambda: self.onMove("p"))

    def initWeb(self):
        web = AnkiWebView()
        # set up custom link handler
        web.setLinkHandler(self.linkHandler)
        return web

    ############ REVIEWS ############

    def setupReviewArea(self):
        """Sets up review area of the preview window"""
        revArea = QWidget()
        review_layout = QVBoxLayout()
        review_layout.setContentsMargins(0, 0, 0, 0)
        revArea.setLayout(review_layout)

        self.revAns = QWidget()
        answer_layout = QHBoxLayout()
        answer_layout.setContentsMargins(0, 0, 0, 0)
        self.revAns.setLayout(answer_layout)

        self.revAnsBtns = []
        self.revAnsLbls = []

        for idx in range(1, 5):
            v = QVBoxLayout()
            btn = QPushButton("", self)
            btn.clicked.connect(lambda _, o=idx: self.onPreviewAnswer(o))
            btn.setToolTip(_("Shortcut key: %s" % str(idx)))
            # primary and secondary hotkeys:
            act1 = QAction(self, triggered=btn.animateClick)
            act1.setShortcut(QKeySequence(PRIMARY_KEYS[idx - 1]))
            act2 = QAction(self, triggered=btn.animateClick)
            act2.setShortcut(QKeySequence(SECONDARY_KEYS[idx - 1]))
            btn.addActions([act1, act2])
            # labels
            btn.setAutoDefault(False)
            btn.setAutoRepeat(False)
            btn.setToolTip(_("Shortcut key: %s" % str(idx)))
            label = QLabel("")
            label.setAlignment(Qt.AlignCenter)
            v.addWidget(label)
            v.addWidget(btn)
            answer_layout.addLayout(v)
            self.revAnsBtns.append(btn)
            self.revAnsLbls.append(label)

        self.revAnsInfo = QLabel()
        self.revAnsInfo.setAlignment(Qt.AlignCenter)

        review_layout.addWidget(self.revAnsInfo)
        review_layout.addWidget(self.revAns)

        return revArea

    def updateRevArea(self, c):
        """Update review area of the previewer"""

        sched = self.mw.col.sched
        early = c.queue != 0 and sched.today < c.due  # not new, not due yet

        ret = False
        ahead = False
        if c.queue in (-1, -2):  # buried or suspended
            self.revAnsInfo.setText(
                transl("Buried or suspended cards cannot be reviewed"))
            self.revAnsInfo.show()
            self.revAns.hide()
            ret = True
        elif early and c.queue == 2:  # early reviews
            if self.config["rev"][1]:  # ahead of schedule enabled
                self.revAnsInfo.setText(
                    transl("Review Ahead of Schedule:"))
                self.revAnsInfo.show()
                self.revAns.show()
                ahead = True
            else:
                self.revAnsInfo.setText(
                    transl("Card is not due, yet"))
                self.revAnsInfo.show()
                self.revAns.hide()
                ret = True
        elif early and c.queue == 3:  # early day learning cards
            self.revAnsInfo.setText(
                transl("Day learning cards cannot be reviewed ahead"))
            self.revAnsInfo.show()
            self.revAns.hide()
            ret = True
        else:  # scheduled reviews, regular learning cards, and new cards
            self.revAnsInfo.hide()
            self.revAns.show()

        if ret:
            self.revArea.show()
            return

        # buttons and shortcuts

        sched.revAnsEarly = ahead  # early review?
        cnt = sched.answerButtons(c)
        if cnt == 2:
            answers = [_("Again"), _("Good"), None, None]
        elif cnt == 3:
            answers = [_("Again"), _("Good"), _("Easy"), None]
        elif cnt == 4:
            answers = [_("Again"), _("Hard"), _("Good"), _("Easy")]
        ease = 0
        for ans, btn, lbl in zip(answers, self.revAnsBtns, self.revAnsLbls):
            ease += 1
            if not ans:
                btn.hide()
                lbl.hide()
                continue
            btn.setText(ans)
            btn.show()
            if not self.mw.col.conf['estTimes']:  # answer times disabled
                lbl.hide()
                continue
            ivl = sched.nextIvlStr(c, ease, True)
            lbl.setText(ivl)
            lbl.show()

        sched.revAnsEarly = False  # reset review mode
        self.revAhead = ahead  # save review mode for onPreviewAnswer

        self.revArea.show()
        self.revAnswers = answers
        self._revTimer = time.time()

    def onPreviewAnswer(self, ease):
        """Answer card with given ease"""

        c = self.b.card
        sched = self.mw.col.sched
        answers = self.revAnswers

        # sanity checks, none of these should ever be triggered
        if not c:  # no card
            return
        if sched.answerButtons(c) < ease:  # wrong ease
            return
        if c.queue in (-1, -2):  # suspended/buried
            return

        # set queue attributes if not set
        for attr in ("newCount", "revCount", "lrnCount"):
            trySetAttribute(sched, attr, 1)

        for attr in ("_newQueue", "_lrnQueue", "_revQueue"):
            trySetAttribute(sched, attr, [])

        if c.queue == 0:  # new
            if c.id not in sched._newQueue:
                sched._newQueue.append(c.id)
        elif c.queue in (1, 3):  # lrn
            if c.id not in sched._lrnQueue:
                sched._lrnQueue.append(c.id)
        elif c.queue == 2:  # new
            if c.id not in sched._revQueue:
                sched._revQueue.append(c.id)

        c.timerStarted = self._revTimer

        print("==========================================")

        sched.revAnsEarly = self.revAhead  # early review?
        sched.answerCard(c, ease)

        print("after review")
        print("c.due", c.due)
        print("c.ivl", c.ivl)
        print("c.factor", c.factor)

        # reset attributes:
        sched.revAnsEarly = False
        c.timerStarted = None
        # save:
        self.mw.autosave()
        self.mw.requireReset()
        self.b.model.reset()
        tooltip(answers[ease - 1], period=2000)

        if self.config["rev"][2]:  # automatically switch to next card
            self.b.onNextCard()

    ############ REVIEWS END ############

    def renderPreview(self, cardChanged=False):
        """
        Generates the preview window content
        """

        oldfocus = None
        cids = self.b.selectedCards()
        nr = len(cids)
        multiple_selected = nr > 1

        if not cids:
            txt = "Please select one or more cards"
            self.web.stdHtml(txt)
            self.updateButtons()
            return

        if cardChanged and not self.both:
            self.state = "question"

        if self.config["rev"][0]:
            # only show review buttons on answer side:
            if self.config["rev"][3] and self.state != "answer":
                self.revArea.hide()
            else:
                self.updateRevArea(self.b.card)

        if cids[0] in self.cards and not multiple_selected:
            # moved focus to another previously selected card
            oldfocus = cids[0]
            cids = self.cards
            nr = len(cids)
            self.multi = nr > 1
            if cardChanged:
                # focus changed without any edits
                if not self.linkClicked and self.multi:
                    # only scroll when coming from browser and multiple cards shown
                    self.scrollToCard(oldfocus)
                self.linkClicked = False
                return
        elif multiple_selected:
            self.multi = True
        else:
            self.multi = False

        if nr >= 200:
            q = ("Are you sure you want to preview <b>{} cards</b> at once? "
                 "This might take a while to render".format(nr))
            ret = askUser(q)
            if not ret:
                return False

        html, css, js = self.renderCards(cids)

        def ti(x):
            return x

        base = getBase(self.mw.col)
        if preview_jsbooster:
            # JS Booster available
            baseUrlText = getBaseUrlText(self.mw.col) + "__previewer__.html"
            stdHtmlWithBaseUrl(self.web,
                               ti(mungeQA(self.mw.col, html)), baseUrlText,
                               css, head=base, js=browserSel + multi_preview_js)
        else:
            # fall back to default
            self.web.stdHtml(
                ti(mungeQA(self.mw.col, html)), css, head=base, js=js)

        if oldfocus and self.multi:
            self.scrollToCard(oldfocus)

        self.cards = cids

        self.updateButtons()

        clearAudioQueue()

        if not self.multi and self.mw.reviewer.autoplay(self.b.card):
            playFromText(html)

    def renderCards(self, cids):
        page = ""
        css = self.mw.reviewer._styles() + preview_css
        html = u"""<div id="{0}" class="card card{1}">{2}</div>"""

        # RegEx to remove multiple imports of external JS/CSS (JS-Booster-specific)
        jspattern = r"""(<script type=".*" src|<style>@import).*(</script>|</style>)"""
        scriptre = re.compile(jspattern)
        js = browserSel

        if self.multi:
            # only apply custom CSS and JS when previewing multiple cards
            html = u"""<div id="{0}" onclick="py.link('focus {0}');toggleActive(this);" \
                   class="card card{1}">{2}</div>"""
            css += multi_preview_css
            js += multi_preview_js

        for idx, cid in enumerate(cids):
            # add contents of each card to preview
            c = self.mw.col.getCard(cid)
            if self.state == "answer":
                ctxt = c.a()
            else:
                ctxt = c.q()
            # Remove subsequent imports of external JS/CSS
            if idx >= 1:
                ctxt = scriptre.sub("", ctxt)
            page += html.format(cid, c.ord + 1, ctxt)

        page = re.sub("\[\[type:[^]]+\]\]", "", page)
        page = runFilter("previewerMungeQA", page)

        return page, css, js

    def updatePreview(self, note):
        replacements = self.renderNote(note)
        if not replacements:
            return False
        cid = None
        for cid, html in replacements.items():
            self.web.eval(u"""
                const elm = document.getElementById('{}');
                elm.innerHTML = {}
                """.format(str(cid), json.dumps(html)))
        if cid:
            self.scrollToCard(cid)

    def renderNote(self, note):
        cards = note.cards()
        replacements = {}
        for card in cards:
            cid = card.id
            if self.state == "answer":
                inner_html = card.a()
            else:
                inner_html = card.q()
            replacements[cid] = inner_html
        return replacements

    def linkHandler(self, url):
        """Executed when clicking on a card"""
        if url.startswith("focus"):
            # bring card into focus
            cid = int(url.split()[1])
            self.linkClicked = True
            self.b.focusCid(cid)
        elif url.startswith("ankiplay"):
            # support for 'Replay Buttons on Card' add-on
            clearAudioQueue()  # stop current playback
            play(url[8:])
        else:
            # handle regular links with the default link handler
            openLink(url)

    def onPrev(self):
        if self.state == "answer" and not self.both:
            self.state = "question"
            self.renderPreview()
        else:
            self.b.onPreviousCard()
        self.updateButtons()

    def onNext(self):
        if self.state == "question":
            self.state = "answer"
            self.renderPreview()
        else:
            self.b.onNextCard()
        self.updateButtons()

    def updateButtons(self):
        """Toggle next/previous buttons"""
        self.b._previewState = self.state
        if self.multi:
            self.btnPrev.setEnabled(False)
            self.btnNext.setEnabled(False)
            return
        current = self.b.currentRow()
        # improve the default behaviour of the previewer:
        canBack = (current > 0 or (current == 0 and self.state == "answer"
                                   and not self.both))
        self.btnPrev.setEnabled(self.b.singleCard and canBack)
        canForward = current < self.b.model.rowCount(None) - 1 or \
                     self.state == "question"
        self.btnNext.setEnabled(self.b.singleCard and canForward)

    def onSidesToggle(self):
        """Switches between preview modes ('front' vs 'back and front')"""
        self.both = self.btnSides.isChecked()
        if self.both:
            self.state = "answer"
        else:
            self.state = "question"
        self.b._renderPreview()

    def onMove(self, target):
        """Move row selection to new target"""
        if target == "s":
            self.b.form.tableView.selectRow(0)
        elif target == "e":
            max = self.b.model.rowCount(None)
            self.b.form.tableView.selectRow(max - 1)
        elif target == "p":
            self.b.onPreviousCard()
        elif target == "n":
            self.b.onNextCard()

    def scrollToCard(self, cid):
        """Adjusts preview window scrolling position to show supplied card"""
        self.web.eval("""
            const elm = document.getElementById('%i');
            const elmRect = elm.getBoundingClientRect();
            const absElmTop = elmRect.top + window.pageYOffset;
            const elmHeight = elmRect.top - elmRect.bottom
            const middle = absElmTop - (window.innerHeight/2) - (elmHeight/2);
            window.scrollTo(0, middle);
            toggleActive(elm);
            """ % cid)
        self.card = self.b.card


def _renderPreviewWrapper(self, cardChanged=False):
    if not self._previewWindow:
        return
    self._previewWindow.renderPreview(cardChanged)


def _openPreview(self):
    """Creates and launches the preview window"""
    pvw = Previewer(self)
    ret = pvw.renderPreview(True)
    if ret is False:
        self.form.previewButton.setChecked(False)
        return
    pvw.show()
    self._previewWindow = self._previewWindow = pvw


def _onClosePreview(self):
    self._previewWindow = self._previewPrev = self._previewNext = None


def onTogglePreview(self):
    """only used to set the link handler after loading the preview window
    (required in order to be compatible with "Replay Buttons on Card")"""
    if self._previewWindow:
        self._previewWindow.web.setLinkHandler(
            self._previewWindow.linkHandler)


def _refreshCurrentCard(self, note):
    self.model.refreshNote(note)
    if not self._previewWindow:
        return
    # multiple cards selected?:
    if self._previewWindow.multi:
        self._previewWindow.updatePreview(note)
    else:
        self._previewWindow.renderPreview(False)


Browser.onTogglePreview = wrap(Browser.onTogglePreview, onTogglePreview)
Browser._openPreview = _openPreview
Browser._onClosePreview = _onClosePreview
Browser._renderPreview = _renderPreviewWrapper
Browser.refreshCurrentCard = _refreshCurrentCard
