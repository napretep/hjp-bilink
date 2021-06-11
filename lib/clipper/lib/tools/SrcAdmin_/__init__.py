import os, json

from PyQt5.QtGui import QIcon

BASEDir = "./resource"
imgDir = ""
jsonDir = ""


def get_json(path="config.json"):  # type: (str)->dict
    fullpath = os.path.join(BASEDir, jsonDir, path)
    obj_dict = json.loads(open(fullpath, "r", encoding="utf-8").read())
    return obj_dict


def get_img_dir(path):
    return (os.path.join(BASEDir, imgDir, path))


class IMGDir:
    def __init__(self):
        self.item_open = get_img_dir("icon_fileopen.png")
        self.item_plus = get_img_dir("icon_addToView.png")
        self.answer = get_img_dir("icon_answer.png")
        self.question = get_img_dir("icon_question.png")
        self.refresh = get_img_dir("icon_refresh.png")
        self.reset = get_img_dir("icon_reset.png")
        self.clipper = get_img_dir("icon_window_clipper.png")
        self.prev = get_img_dir("icon_prev_button.png")
        self.next = get_img_dir("icon_next_button.png")
        self.bag = get_img_dir("icon_page_pick.png")
        self.expand = get_img_dir("icon_fullscreen.png")
        self.config = get_img_dir("icon_configuration.png")
        self.config_reset = get_img_dir("icon_config_reset.png")
        self.close = get_img_dir("icon_close_button.png")
        self.correct = get_img_dir("icon_correct.png")
