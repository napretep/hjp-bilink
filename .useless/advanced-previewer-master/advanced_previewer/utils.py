# -*- coding: utf-8 -*-

"""
This file is part of the Advanced Previewer add-on for Anki

Reusable utilities

Copyright: Glutanimate 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from anki.lang import getLang

ui_strings = {
    "de": {
        "Both sides":
            u"Beide Seiten",
        "Buried or suspended cards cannot be reviewed":
            u"Ausgesetzte Karten können nicht gelernt werden",
        "Review Ahead of Schedule:":
            u"Vorauslernen",
        "Card is not due, yet":
            u"Karte ist noch nicht fällig",
        "Day learning cards cannot be reviewed ahead":
            u"Tageslernkarten können nicht im Voraus gelernt werden"
    }
}


def transl(phrase):
    """Translate string"""
    lang = getLang()
    ldict = ui_strings.get(lang, None)
    if not lang or not ldict:
        return phrase
    return ldict.get(phrase, None) or phrase


def trySetAttribute(obj, attr, value):
    if not hasattr(obj, attr):
        setattr(obj, attr, value)
