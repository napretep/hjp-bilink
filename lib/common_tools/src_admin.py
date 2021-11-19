# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = '$NAME.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/30 9:09'
"""
import dataclasses
import json
import os

from aqt.utils import tooltip


class SrcAdmin:
    ADDON_VERSION="2.0.3"
    addon_name = "hjp_bilink"
    dialog_name = "hjp_bilink_dialog"
    autoreview_update_interval = 3000

    @dataclasses.dataclass
    class Path:
        common_tools: "str" = os.path.abspath(os.path.dirname(__file__))
        lib: "str" = os.path.split(common_tools)[0]
        root: "str" = os.path.split(lib)[0]
        user: "str" = os.path.join(root, "user_files")
        resource: "str" = os.path.join(lib, "resource")
        resource_data: "str" = os.path.join(resource, "data")
        resource_icon: "str" = os.path.join(resource, "icon")
        resource_pic: "str" = os.path.join(resource, "pic")
        helpSite: "str" = "https://gitee.com/huangjipan/hjp-bilink"
        groupSite: "str" = "https://jq.qq.com/?_wv=1027&k=ymObH667"
        introdoc_dir: "str" = os.path.join(resource, "introDoc")
        version_dir: "str" = os.path.join(resource, "versions")
        userconfig: "str" = os.path.join(user, "config.json")
        baseconfig: "str" = os.path.join(root, "baseInfo.json")
        userconfigtemplate: "str" = os.path.join(resource_data, "config.template.json")
        card_model_template:"str" =os.path.join(resource_data,"model.json")
        linkpool_file: "str" = os.path.join(root, "linkpool.json")
        logtext: "str" = os.path.join(root, "log.txt")
        DB_file: "str" = os.path.join(user, "linkInfo.db")
        data_crash_log: "str" = os.path.join(root, "data_crash.txt")
        anchor_CSS_file: "str" = os.path.join(resource_data, "anchor_CSS_default.css")

    class _ImgDir:
        def __init__(self, superior: "SrcAdmin", root: "SrcAdmin"):
            self.superior = superior
            self.root = root
            self.input = os.path.join(self.root.path.resource_icon, "icon_database.png")
            self.anchor = os.path.join(self.root.path.resource_icon, "icon_anchor.png")
            self.info = os.path.join(self.root.path.resource_icon, "icon_info.png")
            self.cancel = os.path.join(self.root.path.resource_icon, "icon_cancel.png")
            self.item_open = os.path.join(self.root.path.resource_icon, "icon_fileopen.png")
            self.item_plus = os.path.join(self.root.path.resource_icon, "icon_addToView.png")
            self.answer = os.path.join(self.root.path.resource_icon, "icon_answer.png")
            self.question = os.path.join(self.root.path.resource_icon, "icon_question.png")
            self.refresh = os.path.join(self.root.path.resource_icon, "icon_refresh.png")
            self.reset = os.path.join(self.root.path.resource_icon, "icon_reset.png")
            self.clipper = os.path.join(self.root.path.resource_icon, "icon_window_clipper.png")
            self.prev = os.path.join(self.root.path.resource_icon, "icon_prev_button.png")
            self.next = os.path.join(self.root.path.resource_icon, "icon_next_button.png")
            self.bag = os.path.join(self.root.path.resource_icon, "icon_page_pick.png")
            self.expand = os.path.join(self.root.path.resource_icon, "icon_fullscreen.png")
            self.config = os.path.join(self.root.path.resource_icon, "icon_configuration.png")
            self.config_reset = os.path.join(self.root.path.resource_icon, "icon_config_reset.png")
            self.close = os.path.join(self.root.path.resource_icon, "icon_close_button.png")
            self.correct = os.path.join(self.root.path.resource_icon, "icon_correct.png")
            self.bookmark = os.path.join(self.root.path.resource_icon, "icon_book_mark.png")
            self.zoomin = os.path.join(self.root.path.resource_icon, "icon_zoom_in.png")
            self.zoomout = os.path.join(self.root.path.resource_icon, "icon_zoom_out.png")
            self.download = os.path.join(self.root.path.resource_icon, "icon_download.png")
            self.goback = os.path.join(self.root.path.resource_icon, "icon_return.png")
            self.stop = os.path.join(self.root.path.resource_icon, "icon_stop.png")
            self.clear = os.path.join(self.root.path.resource_icon, "icon_clear.png")
            self.singlepage = os.path.join(self.root.path.resource_icon, "icon_SinglePage.png")
            self.doublepage = os.path.join(self.root.path.resource_icon, "icon_DoublePage.png")
            self.fit_in_width = os.path.join(self.root.path.resource_icon, "icon_fitin_width.png")
            self.fit_in_height = os.path.join(self.root.path.resource_icon, "icon_fitin_height.png")
            self.mouse_mid_button = os.path.join(self.root.path.resource_icon, "icon_fitin_width.png")
            self.mouse_wheel_zoom = os.path.join(self.root.path.resource_icon, "icon_mouse_wheel_zoom.png")
            self.read = os.path.join(self.root.path.resource_icon, "icon_read.png")
            self.link = os.path.join(self.root.path.resource_icon, "icon_link.png")
            self.link2 = os.path.join(self.root.path.resource_icon, "icon_link2.png")
            self.link2_red = os.path.join(self.root.path.resource_icon, "icon_link2_red.png")
            self.left_direction = os.path.join(self.root.path.resource_icon, "icon_direction_left.png")
            self.right_direction = os.path.join(self.root.path.resource_icon, "icon_direction_right.png")
            self.top_direction = os.path.join(self.root.path.resource_icon, "icon_direction_top.png")
            self.bottom_direction = os.path.join(self.root.path.resource_icon, "icon_direction_bottom.png")
            self.ID_card = os.path.join(self.root.path.resource_icon, "icon_ID_card.png")
            self.qrcode_weixinpay = os.path.join(self.root.path.resource_pic, "weixinpay.jpg")
            self.qrcode_alipay = os.path.join(self.root.path.resource_pic, "alipay.jpg")
            self.heart = os.path.join(self.root.path.resource_icon, "icon_heart.png")
            self.tree = os.path.join(self.root.path.resource_icon, "icon_tree.png")
            self.list = os.path.join(self.root.path.resource_icon, "icon_list.png")
            self.box = os.path.join(self.root.path.resource_icon, "icon_box.png")
            self.tag = os.path.join(self.root.path.resource_icon, "icon_tag.png")
            self.robot_black = os.path.join(self.root.path.resource_icon,"icon_robot_black.png")
            self.robot_red = os.path.join(self.root.path.resource_icon,"icon_robot_red.png")
            self.robot_green = os.path.join(self.root.path.resource_icon,"icon_robot_green.png")

    @dataclasses.dataclass
    class _ShortCut:
        shortcut_browserTableSelected_link = "Alt+1"
        shortcut_browserTableSelected_unlink = "Alt+2"
        shortcut_browserTableSelected_insert = "Alt+3"
        shortcut_inputFile_clear = "Alt+4"
        shortcut_inputDialog_open = "Alt+`"
        shortcut_copylink = "Alt+q"

    class _Config:
        def __init__(self, superior: "SrcAdmin"):
            self.superior = superior
            self._root = superior
            self.base = self._Base(self, self._root)

        class _Base:
            def __init__(self, superior: "SrcAdmin._Config", root: "SrcAdmin"):
                self.superior = superior
                self.root = root
                self.VERSION = "0.12"

            @property
            def get_base_config(self):
                data = json.load(open(self.root.path.baseconfig, "r", encoding="utf-8"))
                return data



    instance = None

    @classmethod
    def start(cls):
        """cls就相当于是self,这里的意思是如果instance不存在则创建一个,返回instance,这是单例模式"""
        # print(cls.instance)
        if cls.instance is None:
            cls.instance = cls()
            cls.path = cls.Path()
            # cls.config = cls._Config(cls.instance)
            cls.ImgDir = cls._ImgDir(cls.instance, cls.instance)
        return cls.instance

    pass


if __name__ == "__main__":
    a = SrcAdmin.start()
    print(a._ShortCut.shortcut_copylink)