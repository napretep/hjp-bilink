import os, json

from PyQt5.QtGui import QIcon
from aqt.utils import showInfo, aqt_data_folder


class Get:
    instance = None
    dir_SrcAdmin_ = os.path.dirname(__file__)
    dir_tools = os.path.split(dir_SrcAdmin_)[0]
    dir_lib = os.path.split(dir_tools)[0]
    dir_clipper = os.path.split(dir_lib)[0]
    dir_lib0 = os.path.split(dir_clipper)[0]
    dir_root = os.path.split(dir_lib0)[0]
    dir_user_files = "user_files"
    dir_resource = "resource"
    dir_img = ""
    dir_json = ""

    def json_dict(cls, path="config.json"):  # type: (str)->dict
        fullpath = os.path.join(cls.dir_clipper, cls.dir_resource, cls.dir_json, path)
        obj_dict = json.loads(open(fullpath, "r", encoding="utf-8").read())
        return obj_dict

    def config_dict(cls, configname):
        if configname == 'clipper':
            path = "clipper.config.json"
            fullpath = cls.json_dir("clipper")
            # print(fullpath)
            if not os.path.exists(fullpath):
                print(f"{fullpath}不存在,重建中")
                default_path = cls.json_dir("clipper.template")
                default_dict_str = open(default_path, "r", encoding="utf-8").read()
                cls.save_dict(fullpath, default_dict_str)
            config = json.loads(open(fullpath, "r", encoding="utf-8").read())
            # print(config)
            return config
        elif configname == "clipper.template":
            fullpath = cls.json_dir(configname)
            config = json.loads(open(fullpath, "r", encoding="utf-8").read())
            return config
        else:
            raise ValueError("没有对应的文件！")

    def save_dict(self, olddict_path, newdict_str):
        f = open(olddict_path, "w", encoding="utf-8")
        f.write(newdict_str)
        f.close()

    def json_dir(cls, jsonname):
        if jsonname == "clipper":
            return os.path.join(cls.dir_root, cls.dir_user_files, "clipper.config.json")
        if jsonname == "clipper.template":
            return os.path.join(cls.dir_clipper, cls.dir_resource, cls.dir_json, "config.template.json")

    def img_dir(cls, path):
        return (os.path.join(cls.dir_clipper, cls.dir_resource, cls.dir_img, path))

    @classmethod
    def _(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


class JSONDir:
    def __init__(self):
        self.clipper = Get._().json_dir("clipper")
        self.clipper_template = Get._().json_dir("clipper.template")

class IMGDir:
    def __init__(self):
        self.item_open = Get._().img_dir("icon_fileopen.png")
        self.item_plus = Get._().img_dir("icon_addToView.png")
        self.answer = Get._().img_dir("icon_answer.png")
        self.question = Get._().img_dir("icon_question.png")
        self.refresh = Get._().img_dir("icon_refresh.png")
        self.reset = Get._().img_dir("icon_reset.png")
        self.clipper = Get._().img_dir("icon_window_clipper.png")
        self.prev = Get._().img_dir("icon_prev_button.png")
        self.next = Get._().img_dir("icon_next_button.png")
        self.bag = Get._().img_dir("icon_page_pick.png")
        self.expand = Get._().img_dir("icon_fullscreen.png")
        self.config = Get._().img_dir("icon_configuration.png")
        self.config_reset = Get._().img_dir("icon_config_reset.png")
        self.close = Get._().img_dir("icon_close_button.png")
        self.correct = Get._().img_dir("icon_correct.png")
        self.bookmark = Get._().img_dir("icon_book_mark.png")
        self.zoomin = Get._().img_dir("icon_zoom_in.png")
        self.zoomout = Get._().img_dir("icon_zoom_out.png")
        self.download = Get._().img_dir("icon_download.png")


if __name__ == "__main__":
    print(Get._().img_dir(""))
