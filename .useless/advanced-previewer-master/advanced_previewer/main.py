# -*- coding: utf-8 -*-

"""
This file is part of the Advanced Previewer add-on for Anki

Main Module, hooks add-on methods into Anki

Copyright: Glutanimate 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from aqt.qt import *
from aqt import mw

from anki.hooks import addHook

from .config import loadConfig, AdvPrevOptions


# Menus


def onAdvPrevOptions(mw):
    """Invoke global config dialog"""
    dialog = AdvPrevOptions(mw)
    dialog.exec_()


options_action = QAction("A&dvanced Previewer Options...", mw)
options_action.triggered.connect(lambda _, m=mw: onAdvPrevOptions(m))
mw.form.menuTools.addAction(options_action)


# Add-on setup


def setupAddon():
    loadConfig()


# Monkey patches and hooks into Anki's default methods


addHook("profileLoaded", setupAddon)
