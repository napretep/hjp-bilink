# -*- coding: utf-8 -*-

"""
This file is part of the Advanced Previewer add-on for Anki

Add-on configuration

Copyright: Glutanimate 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from aqt.qt import *
from aqt import mw

from .forms import settings

# dsp: show both sides by default
# rev: card review settings
default_prefs = {
    "dsp": [False],
    "rev": [False, False, False, False],
    "version": 0.4
}


def loadConfig():
    """Load and/or create add-on prefs"""
    prefs = mw.pm.profile
    default = default_prefs
    if 'advprev' not in prefs:
        # create initial prefs
        prefs['advprev'] = default
        mw.pm.save()

    elif prefs['advprev']['version'] < default['version']:
        print("Updating advprev prefs from earlier add-on release")
        for key in list(default.keys()):
            if key not in prefs['advprev']:
                prefs['advprev'][key] = default[key]
        prefs['advprev']['version'] = default['version']
        # insert other update actions here:
        prefs['advprev']['nxt'] = default_prefs["rev"]
        mw.pm.save()

    return mw.pm.profile['advprev']


class AdvPrevOptions(QDialog):
    """Global options dialog"""

    def __init__(self, mw):
        super(AdvPrevOptions, self).__init__(parent=mw)
        # load qt-designer form:
        self.f = settings.Ui_Dialog()
        self.f.setupUi(self)
        self.f.textBrowser.setOpenExternalLinks(True)
        self.f.cb_rev_main.stateChanged.connect(self.onCbRevToggle)
        self.f.buttonBox.accepted.connect(self.onAccept)
        self.f.buttonBox.rejected.connect(self.onReject)
        self.f.buttonBox.button(
            QDialogButtonBox.RestoreDefaults).clicked.connect(self.onRestore)
        self.f.rev_cbs = (self.f.cb_rev_main, self.f.cb_rev_ahd,
                          self.f.cb_rev_nxt, self.f.cb_rev_ans)
        config = loadConfig()
        self.setupValues(config)

    def setupValues(self, config):
        self.f.cb_dpl_qa.setChecked(config["dsp"][0])
        for idx, cb in enumerate(self.f.rev_cbs):
            cb.setChecked(config["rev"][idx])
        self.onCbRevToggle(self.f.cb_rev_main.isChecked())

    def onCbRevToggle(self, state):
        for i in self.f.rev_cbs[1:]:
            i.setEnabled(state)

    def onAccept(self):
        config = loadConfig()
        config['dsp'][0] = self.f.cb_dpl_qa.isChecked()
        config['rev'] = [i.isChecked() for i in self.f.rev_cbs]
        mw.pm.save()
        self.close()

    def onRestore(self):
        self.setupValues(default_prefs)

    def onReject(self):
        self.close()
