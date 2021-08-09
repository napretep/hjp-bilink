# -*- coding: utf-8 -*-

"""
This file is part of the Advanced Previewer add-on for Anki

Modifications to Anki's card scheduler

Copyright: Glutanimate 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from __future__ import division

from anki.sched import Scheduler
from anki.hooks import wrap


def nextRevIvl(self, card, ease, _old):
    "Ideal next interval for CARD, given EASE. Adjusted for early cards."

    if not getattr(self, "revAnsEarly", False):  # regular review
        return _old(self, card, ease)  # go back to default method
    if self.today >= card.due:  # sanity check, should never be triggered
        return _old(self, card, ease)

    conf = self._revConf(card)

    # LEGEND

    # card.factor:  ease factor of card per mille (e.g. 2500 for 250%)
    # card.ivl:     card interval in days
    # card.due:     due date in days since collection was created
    # self.today:   today's date in days since collection was created
    # conf[ease4]:  ease bonus factor for cards marked as easy (e.g. 1.5)

    # EASE FACTOR CALCULATION

    # This is the formula used in _dynIvlBoost() for studying ahead
    # (ease averaged with "hard" ease, leading to a potentially
    # severe penalty for reviewing cards only a few days ahead of
    # schedule)

    # fct = ((card.factor/1000)+1.2)/2

    # Instead, we use the formula for regular reviews (no ease penalty):

    fct = card.factor / 1000

    # (credits to rjgoif on the Anki support forums for discovering
    # this issue and the potential solution)

    # ELAPSED TIME CALCULATION

    # In calculating the new interval below, we factor in how many days
    # of the current interval have actually passed:

    elapsed = card.ivl - (card.due - self.today)

    # INTERVAL CALCULATION

    # These are based on the formulas for regular reviews, with two major
    # differences:
    #
    # 1.) We don't apply any ivl-specific weighting factor to the difference
    #     between due date and actual review date. I've experimented with
    #     using weighting factors, but I haven't been able to find any sensible
    #     values to apply
    # 2.) Instead of using self._constrainedivl, which factors in the
    #     interval factor and increments each ivl by at least one day, we
    #     use a simpler approach with max(), similar to the default calculation
    #     for studying ahead

    # As you can see, the minimum interval across all eases is the current
    # interval of the card. This follows how _dynIvlBoost() works.
    # For that reason the intervals you will be presented with will often be
    # the same for all cards (just like the custom study option only offers
    # "good" as an answer for cards studied ahead).
    #
    # As the scheduled due date draws closer these intervals will start to
    # diverge, ever coming closer to the intervals you would see if you
    # were to review the card when it's actually due

    ivl2 = int(max(elapsed * 1.2, card.ivl, 1))  # hard (default fct = 1.2)
    ivl3 = int(max(elapsed * fct, ivl2, 1))  # good
    ivl4 = int(max(elapsed * fct * conf['ease4'], ivl3, 1))  # easy

    print("--------------------------------")
    print("card.ivl", card.ivl)
    print("elapsed", elapsed)
    print("delta to due", card.due - self.today)
    print("fct", fct)
    print("ivl2", ivl2)
    print("ivl3", ivl3)
    print("ivl4", ivl4)

    if ease == 2:
        interval = ivl2
    elif ease == 3:
        interval = ivl3
    elif ease == 4:
        interval = ivl4
    # interval capped?
    return min(interval, conf['maxIvl'])


Scheduler._nextRevIvl = wrap(Scheduler._nextRevIvl, nextRevIvl, "around")
