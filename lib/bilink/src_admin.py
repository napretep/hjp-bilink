import dataclasses
import json
import os


class SrcAdmin:
    addon_name = "hjp_bilink"
    dialog_name = "hjp_bilink_dialog"

    @dataclasses.dataclass
    class _Path:
        bilink: "str" = os.path.abspath(os.path.dirname(__file__))
        lib: "str" = os.path.split(bilink)[0]
        root: "str" = os.path.split(lib)[0]
        user: "str" = os.path.join(root, "user_files")
        userconfig: "str" = os.path.join(user, "config.json")
        baseconfig: "str" = os.path.join(root, "baseInfo.json")
        linkpooljson: "str" = os.path.join(root, "input.json")
        logtext: "str" = os.path.join(root, "log.txt")
        resource: "str" = os.path.join(lib, "resource")
        resource_data: "str" = os.path.join(resource, "data")
        resource_icon: "str" = os.path.join(resource, "icon")
        userconfigtemplate: "str" = os.path.join(resource_data, "config.template.json")
        helpSite: "str" = "https://gitee.com/huangjipan/hjp-bilink"
        groupSite: "str" = "https://jq.qq.com/?_wv=1027&k=ymObH667"
        introdoc_dir: "str" = os.path.join(resource, "introDoc")
        version_dir: "str" = os.path.join(resource, "versions")

    class _ImgDir:
        def __init__(self, superior: "SrcAdmin", root: "SrcAdmin"):
            self.superior = superior
            self.root = root
            self.input = os.path.join(self.root.path.resource_icon, "icon_database.png")
            self.anchor = os.path.join(self.root.path.resource_icon, "icon_anchor.png")
            self.config = os.path.join(self.root.path.resource_icon, "icon_configuration.png")

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
            self.user = self._User(self, self._root)
            self.base = self._Base(self, self._root)
            self.template = self._Template(self, self._root)

        class _Base:
            def __init__(self, superior: "SrcAdmin._Config", root: "SrcAdmin"):
                self.superior = superior
                self.root = root
                self.VERSION = "0.12"

            @property
            def get_base_config(self):
                data = json.load(open(self.root.path.baseconfig, "r", encoding="utf-8"))
                return data

        @dataclasses.dataclass
        class _User:

            def __init__(self, superior: "SrcAdmin._Config", root: "SrcAdmin"):
                self.superior = superior
                self.root = root
                self.linkInfoStorageLocation: "str" = self.get_config[
                    "linkInfoStorageLocation"]  # 控制链接的存储地点,默认是0,即sqlite存储
                self.defaultUnlinkMode: "str" = self.get_config["defaultUnlinkMode"]  # 默认的取消链接模式
                self.defaultInsertMode: "str" = self.get_config["defaultInsertMode"]  # 默认的插入模式
                self.defaultLinkMode: "str" = self.get_config["defaultLinkMode"]  # 默认的链接模式
                self.readDescFieldPosition: "str" = self.get_config["readDescFieldPosition"]  # 默认描述读取的字段位置
                self.appendNoteFieldPosition: "str" = self.get_config[
                    "appendNoteFieldPosition"]  # 如果选择存储在field中,则会根据这个参数选择存储在卡片的哪一个field
                self.descMaxLength: "str" = self.get_config["descMaxLength"]  # 默认描述读取的最大字符长度
                self.button_appendTo_AnchorId: "str" = self.get_config["button_appendTo_AnchorId"]  # 默认把绿色的悬浮下拉菜单加在什么地方
                self.anchorCSSFileName: "str" = self.get_config["anchorCSSFileName"]  # 悬浮下拉的菜单的样式文件地址
                self.VERSION: "str" = self.get_config["VERSION"]  # 版本
                # 删除文内链接,当我们需要提取描述时.
                self.delete_intext_link_when_extract_desc: "int" = self.get_config[
                    "delete_intext_link_when_extract_desc"]

            @property
            def get_config(self) -> dict:
                data = json.load(open(self.root.path.userconfig, "r", encoding="utf-8"))
                return data

            def __repr__(self):
                return self.get_config.__str__()

        class _Template:
            def __init__(self, superior: "SrcAdmin._Config", root: "SrcAdmin"):
                self.superior = superior
                self.root = root
                self.linkInfoStorageLocation: "str" = self.get_config[
                    "linkInfoStorageLocation"]  # 控制链接的存储地点,默认是0,即sqlite存储
                self.defaultUnlinkMode: "str" = self.get_config["defaultUnlinkMode"]  # 默认的取消链接模式
                self.defaultInsertMode: "str" = self.get_config["defaultInsertMode"]  # 默认的插入模式
                self.defaultLinkMode: "str" = self.get_config["defaultLinkMode"]  # 默认的链接模式
                self.readDescFieldPosition: "str" = self.get_config["readDescFieldPosition"]  # 默认描述读取的字段位置
                self.appendNoteFieldPosition: "str" = self.get_config[
                    "appendNoteFieldPosition"]  # 如果选择存储在field中,则会根据这个参数选择存储在卡片的哪一个field
                self.descMaxLength: "str" = self.get_config["descMaxLength"]  # 默认描述读取的最大字符长度
                self.button_appendTo_AnchorId: "str" = self.get_config["button_appendTo_AnchorId"]  # 默认把绿色的悬浮下拉菜单加在什么地方
                self.anchorCSSFileName: "str" = self.get_config["anchorCSSFileName"]  # 悬浮下拉的菜单的样式文件地址
                self.VERSION: "str" = self.get_config["VERSION"]  # 版本
                # 删除文内链接,当我们需要提取描述时.
                self.delete_intext_link_when_extract_desc: "int" = self.get_config[
                    "delete_intext_link_when_extract_desc"]

            @property
            def get_config(self) -> dict:
                data = json.load(open(self.root.path.userconfigtemplate, "r", encoding="utf-8"))
                return data

            def __repr__(self):
                return self.get_config.__str__()

    instance = None

    @classmethod
    def start(cls):
        """cls就相当于是self,这里的意思是如果instance不存在则创建一个,返回instance,这是单例模式"""
        # print(cls.instance)
        if cls.instance is None:
            cls.instance = cls()
            cls.path = cls._Path()
            cls.config = cls._Config(cls.instance)
            cls.ImgDir = cls._ImgDir(cls.instance, cls.instance)
        return cls.instance

    pass


if __name__ == "__main__":
    a = SrcAdmin.start()
    print(a._ShortCut.shortcut_copylink)
