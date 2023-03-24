# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'text.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/3/16 1:23'
"""

import json , os, sys
dev_metaJson = "./meta.json"
local_metaJson = "../hjp_linkmaster/meta.json"
is_win = sys.platform.startswith("win32")


def modify_meta(path,disabled=False):
    data = json.load(open(path, "r", encoding="utf-8"))
    data["disabled"] = disabled
    json.dump(data, open(path, "w", encoding="utf-8"))

def start_dev():
    modify_meta(dev_metaJson)

def start_local():
    modify_meta(dev_metaJson,True)


if __name__ == "__main__":
    if is_win:
        start_local()
        # start_dev()
        os.system("anki")
    pass