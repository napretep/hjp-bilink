import abc, dataclasses

from .. import G, language
from ..compatible_import import *






译 = language.Translate
class 逻辑:
    @staticmethod
    def 缺省值(值, 规则: "Callable", 缺省值=None):
        try:
            结果 = 规则(值)
            if 结果:
                return 结果
            else:
                return 缺省值
        except:
            return 缺省值


class 通用:
    class 窗口:
        @staticmethod
        def 半开(组件: "QWidget", 左右="左",中心化=True,长比例=0.4,宽比例=0.8):
            桌面尺寸 = QApplication.instance().screens()[
                0].availableGeometry()  # https://blog.csdn.net/dgxl22/article/details/121725550
            桌面宽度 = 桌面尺寸.width()
            桌面高度 = 桌面尺寸.height()
            桌面横坐标 = 桌面尺寸.x()
            桌面纵坐标 = 桌面尺寸.y()
            桌面中心 = [int((桌面横坐标 + 桌面宽度) / 2), int((桌面纵坐标 + 桌面高度) / 2)]
            组件长宽 = [int(桌面尺寸.width() * 0.4), int(桌面尺寸.height() * 0.8)]

            组件坐标 = [桌面中心[0] if 左右 == "右" else int(桌面宽度 * 0.1), int(桌面高度 * 0.1)]

            组件.resize(*组件长宽)
            组件.move(*组件坐标)

class Map:
    @staticmethod
    def do(li: "iter", func: "callable"):
        return list(map(func, li))


class Filter:
    @staticmethod
    def do(li: "iter", func: "callable"):
        return list(filter(func, li))

class 平行导入:
    @property
    def Configs(self):
        from . import Config
        return Config
    @property
    def link(self):
        from . import link
        return link
    @property
    def Gview(self):
        from . import Gview
        return Gview

    @property
    def Dialogs(self):
        from . import Dialogs
        return Dialogs.Dialogs

    @property
    def card(self):
        from . import card
        return card
    @property
    def browser(self):
        from .import browser
        return browser


imports = 导入 = 平行导入()


def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


class Utils(object):
    @dataclasses.dataclass
    class MenuType:
        ankilink = 0

    class LOG:
        # logger = logger(__name__)
        # file_write = write_to_log_file

        @staticmethod
        def file_clear():
            f = open(G.src.path.logtext, "w", encoding="utf-8")
            f.write("")

        @staticmethod
        def exists():
            return os.path.exists(G.src.path.logtext)

    # @staticmethod
    # def 主动备份():
    #     path,ok = QFileDialog.getExistingDirectory()

    @staticmethod
    def 正则合法性(值):
        try:
            re.compile(值)
            return True
        except:
            return False

    @staticmethod
    def make_backup_file_name(filename, path=""):
        file = "backup_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "_" + os.path.split(filename)[-1]
        if not path:
            return os.path.join(*os.path.split(filename)[:-1], file)
        else:
            return os.path.join(path, file)

    @staticmethod
    def percent_calc(total, count, begin, ratio):
        return math.ceil(count / total * ratio) + begin

    @staticmethod
    def emptystr(s):
        return not re.match(r"\S", s)

    @staticmethod
    def tooltip(s):
        if G.ISLOCALDEBUG:
            Utils.print(s)
        else:
            tooltip(s)

    @staticmethod
    def showInfo(s):
        if G.ISDEBUG:
            showInfo(s)

    @staticmethod
    def rect_center_pos(rect: 'Union[QRectF,QRect]'):
        return QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)

    # @staticmethod
    # def output():

    # noinspection PyUnresolvedReferences
    @staticmethod
    def print(*args, need_timestamp=True, need_logFile=True,simple=True, **kwargs):

        if G.ISDEBUG:

            caller1 = sys._getframe(1).f_code.co_name
            caller1_filename:"str" = sys._getframe(1).f_code.co_filename
            caller1_lineNo = sys._getframe(1).f_lineno
            caller2 = sys._getframe(2).f_code.co_name
            caller2_filename:"str" = sys._getframe(2).f_code.co_filename
            caller2_lineNo = sys._getframe(2).f_lineno
            if need_timestamp:
                ts = (datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
            else:
                ts = ""
            head = f"{ts}|{caller2_filename.replace(G.src.path.addons21,'')}:{caller2_lineNo}:{caller2}\n>>{caller1_filename.replace(G.src.path.addons21,'')}:{caller1_lineNo}:{caller1}:\n"
            head2 = "hjp-linkmaster-log:" if not simple else head
            if need_logFile:
                f = open(G.src.path.logtext, "a", encoding="utf-8")
                if not simple:
                    traceback.print_stack(file=f)
                print(head2,*args, **kwargs, file=f)
            else:
                print(head2, *args, **kwargs)

    @staticmethod
    def 字典默认键值对(默认值, 键名, 对应值字典, 类型对照: "dict" = None):
        字典键名 = G.safe.baseClass.枚举命名
        if not 对应值字典 or not 键名 in 对应值字典:
            return 默认值
        else:
            if 类型对照:
                if type(对应值字典[键名]) in 字典键名.值类型.字典[类型对照[键名]]:
                    return 对应值字典[键名]
                else:
                    return 默认值
            else:
                return 对应值字典[键名]
        # if not 对应值 or 键名 not in 对应值:
        #     return 默认值
        # elif 类型对照 and type(对应值) in 字典键名.值类型.字典[类型对照[键名]]:
        #     return 对应值
        #
        #
        # return 默认值 if not 对应值 or 键名 not in 对应值 else 对应值[键名]

    @staticmethod
    def 字典缺省值填充器(默认值字典: dict, 对应值字典: "Optional[dict]" = None, 类型对照=None):
        新值 = {}
        for 键, 值 in 默认值字典.items():
            新值[键] = Utils.字典默认键值对(值, 键, 对应值字典, 类型对照)
        return 新值

    @staticmethod
    def 时间戳转日期(时间戳):
        return datetime.datetime.fromtimestamp(时间戳)

    @staticmethod
    def 日期转时间戳(日期):
        """
        日期为: YYYY-MM-DD格式
        """
        return int(time.mktime(time.strptime(日期, "%Y-%m-%d")))

    @staticmethod
    def 大文本提示框(文本, 取消模态=False, 尺寸=(600, 400)):
        字典键名 = G.safe.baseClass.枚举命名

        _ = 字典键名.砖

        组合 = {_.框: QHBoxLayout(), _.子: [{_.件: QTextBrowser()}]}
        组合[_.子][0][_.件].setHtml(Utils.html默认格式(文本))
        # noinspection PyArgumentList
        对话框: QDialog = G.safe.widgets.组件定制.组件组合(组合, QDialog())
        if 取消模态:
            对话框.setModal(False)
            对话框.setWindowModality(Qt.WindowModality.NonModal)
        对话框.resize(*尺寸)
        对话框.exec()
        pass

    @staticmethod
    def html默认格式(内容):
        文本2 = "<p>" + 内容.replace("\n", "<br>") + "</p>"
        return """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <title></title>
        <style>
        </style>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Microsoft/vscode/extensions/markdown-language-features/media/markdown.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Microsoft/vscode/extensions/markdown-language-features/media/highlight.css">
        <style>
        body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe WPC', 'Segoe UI', system-ui, 'Ubuntu', 'Droid Sans', sans-serif;
        font-size: 17px;
        line-height: 1.6;
        }
        </style>
        <style>
        .task-list-item { list-style-type: none; } .task-list-item-checkbox { margin-left: -20px; vertical-align: middle; }
        </style>
        </head>
        <body class="vscode-body vscode-light">
        """ + 文本2 + """
        </body>
        </html>
                """

    class 时间处理:

        @staticmethod
        def 日偏移(日期=None, 偏移量: int = 0):

            """
            可用的指标: days
            返回时间戳"""
            if 日期 is None:
                日期 = datetime.datetime.today().date()
            偏移时间 = 日期 + datetime.timedelta(days=偏移量)
            时间戳 = int(time.mktime(偏移时间.timetuple()))
            return 时间戳

        @staticmethod
        def 月偏移(日期=None, 偏移量=0):
            if 日期 is None:
                日期 = datetime.datetime.today().date()
            日期年份 = 日期.timetuple().tm_year
            日期月份 = 日期.timetuple().tm_mon
            所求月份 = 12 if (日期月份 + 偏移量) % 12 == 0 else (日期月份 + 偏移量) % 12
            所求年份 = math.ceil((日期月份 + 偏移量) / 12) - 1 + 日期年份
            时间戳 = int(time.mktime(datetime.datetime(所求年份, 所求月份, 1).timetuple()))
            return 时间戳

        @staticmethod
        def 周偏移(指标=0):
            pass

        @staticmethod
        def 今日():
            return Utils.时间处理.日偏移()

        @staticmethod
        def 昨日():
            return Utils.时间处理.日偏移(None, -1)

        @staticmethod
        def 三天前():
            return Utils.时间处理.日偏移(None, -3)

        @staticmethod
        def 本周():
            今天周几 = datetime.datetime.today().timetuple().tm_wday
            return Utils.时间处理.日偏移(None, -今天周几)

        @staticmethod
        def 上周():
            今天周几 = datetime.datetime.today().timetuple().tm_wday
            return Utils.时间处理.日偏移(None, -今天周几 - 7)

        @staticmethod
        def 本月():
            return Utils.时间处理.月偏移(None, 0)

        @staticmethod
        def 一个月前():
            return Utils.时间处理.月偏移(None, -1)

        @staticmethod
        def 三个月前():
            """本月,上月,上上月
            3 2 1 12 11
            """
            return Utils.时间处理.月偏移(None, -3)

        @staticmethod
        def 六个月前():
            return Utils.时间处理.月偏移(None, -6)
            # 现在 = time.localtime()
            # time.mktime((现在.tm_year,现在.tm_mon,现在.tm_mday-现在.tm_wday,0,0,0,0,0,0))

    class 版本:

        @dataclasses.dataclass
        class 模型:
            version: "str"
            installed_at: "int" = int(time.time())

        @staticmethod
        def 版本冲突():
            本地版地址 = G.src.path.local_version
            网络版地址 = G.src.path.web_version
            开发版地址 = G.src.path.dev_version
            当前插件地址 = G.src.path.root
            if 当前插件地址 == 开发版地址:
                tooltip("dev mode")
                return False
            elif Utils.版本.开发版被启用():
                tooltip("dev mode")
                return True
            elif Utils.版本.本地版被启用() and Utils.版本.网络版被启用() and 当前插件地址 == 本地版地址:
                showInfo(译.检测到同时启用了本地版与网络版插件)
                return True

            return False
        @staticmethod
        def 网络版被启用():
            网络版地址 = G.src.path.web_version
            if not os.path.exists(网络版地址):
                return False
            else:
                return json.load(open(os.path.join(网络版地址, "meta.json")))["disabled"] == False
            pass

        @staticmethod
        def 本地版被启用():
            本地版地址 = G.src.path.local_version
            if not os.path.exists(本地版地址):
                return False
            else:
                return json.load(open(os.path.join(本地版地址, "meta.json")))["disabled"] == False
            pass
            pass

        @staticmethod
        def 开发版被启用():
            开发版地址 = G.src.path.dev_version
            if not os.path.exists(开发版地址):
                return False
            else:
                data = json.load(open(os.path.join(开发版地址, "meta.json")))
                # tooltip("disabled="+data["disabled"])
                return not data["disabled"]
            pass


        @staticmethod
        def 检查():
            版本路径 = G.src.path.current_version
            当前版本 = G.src.ADDON_VERSION
            if not os.path.exists(版本路径):
                Utils.版本.发出提醒()
                Utils.版本.创建版本文件()
            else:
                版本数据 = Utils.版本.读取版本文件()[-1]
                if 版本数据["version"] != 当前版本:
                    Utils.版本.发出提醒()
                    Utils.版本.添加版本()

        @staticmethod
        def 发出提醒():
            code = QMessageBox.information(None, 译.新版本介绍, 译.是否查看更新日志, QMessageBox_StandardButton.Yes | QMessageBox_StandardButton.No)
            if code == QMessageBox_StandardButton.Yes:
                Utils.版本.打开网址()

        @staticmethod
        def 打开网址():
            QDesktopServices.openUrl(QUrl("https://vu2emlw0ia.feishu.cn/docx/GCl6djBtiouRumxbbB4cbfnHn4c"))
            pass

        @staticmethod
        def 创建版本文件():
            版本路径 = G.src.path.current_version
            当前版本 = G.src.ADDON_VERSION
            Utils.版本.保存版本文件([Utils.版本.模型(当前版本).__dict__])

        @staticmethod
        def 添加版本():
            版本路径 = G.src.path.current_version
            当前版本 = G.src.ADDON_VERSION
            if not os.path.exists(版本路径):
                Utils.版本.创建版本文件()
            else:
                版本表 = Utils.版本.读取版本文件()
                版本表.append(Utils.版本.模型(当前版本).__dict__)
                Utils.版本.保存版本文件(版本表)

        @staticmethod
        def 保存版本文件(对象):
            版本路径 = G.src.path.current_version
            json.dump(对象, open(版本路径, "w", encoding="utf-8"))

        @staticmethod
        def 读取版本文件():
            版本路径 = G.src.path.current_version
            return sorted(json.load(open(版本路径, "r", encoding="utf-8")), key=lambda x: x["installed_at"])

class UUID:
    标准长度 = len(str(uuid.uuid4()))
    @staticmethod
    def by_random(length=8):
        myid = str(uuid.uuid4())[0:length]
        return myid

    @staticmethod
    def by_hash(s):
        return str(uuid.uuid3(uuid.NAMESPACE_URL, s))

    @staticmethod
    def 任意长度(长度):
        UUID串 = ""
        几个UUID = math.ceil(长度/UUID.标准长度)
        最后一个UUID长度 = 长度 % UUID.标准长度 if  长度 % UUID.标准长度>0 else UUID.标准长度
        for i in range(几个UUID):
            if i != 几个UUID-1:
                UUID串 += UUID.by_random(UUID.标准长度)
            else:
                UUID串 += UUID.by_random(最后一个UUID长度)
        return UUID串

class HTML:
    @staticmethod
    def file_protocol_support(html_string):
        root = BeautifulSoup(html_string, "html.parser")
        href_is_file_li: "List[element.Tag]" = root.select('[href^="file://"]')
        style = root.new_tag("style", attrs={"class": G.src.pdfurl_style_class_name})
        style.string = f".{G.src.pdfurl_class_name}{{{导入.Configs.Config.get().PDFLink_style.value}}}"
        root.insert(1, style)
        if len(href_is_file_li) > 0:
            for href in href_is_file_li:
                filestr = href["href"]
                href["onclick"] = f"""javascript:pycmd("{filestr}")"""
                href["href"] = ""
                href["class"] = G.src.pdfurl_class_name
        return root.__str__()

    @staticmethod
    def TextContentRead(html):
        # return HTML_txtContent_read(html)
        # from ..bilink.in_text_admin.backlink_reader import BackLinkReader
        BackLinkReader = G.safe.in_text_admin.backlink_reader.BackLinkReader

        cfg = G.safe.configsModel.ConfigModel()
        root = BeautifulSoup(html, "html.parser")
        list(map(lambda x: x.extract(), root.select(".hjp_bilink.ankilink.button")))
        text = root.getText()
        if cfg.delete_intext_link_when_extract_desc.value:
            待替换的html文本 = text
            intext列表 = BackLinkReader(html_str=text).backlink_get()
            待删除的intext列表 = []
            print(intext列表)
            for intext链接信息 in intext列表: # 将内链接替换成随机字符, 然后删除
                print("当前处理的intextlink=",intext链接信息)
                span = intext链接信息["span"]
                随机字符 = UUID.任意长度(span[1]-span[0])
                待删除的intext列表.append(随机字符)
                待替换的html文本 = 待替换的html文本[0:span[0]]+随机字符+待替换的html文本[span[1]:]
            if 待删除的intext列表:
                text = re.sub("|".join(待删除的intext列表), "", 待替换的html文本)
        if not re.search("\S", text):
            a = root.find("img")
            if a is not None:
                text = a.attrs["src"]

        return text

    @staticmethod
    def injectToWeb(htmltext, card, kind):
        if kind in [
                "previewQuestion",
                "previewAnswer",
                "reviewQuestion",
                "reviewAnswer"
        ]:
            from .HTMLbutton_render import HTMLbutton_make
            html_string = HTMLbutton_make(htmltext, card)

            return html_string
        else:
            return htmltext

    @staticmethod
    def cardHTMLShadowDom(innerHTML: "str", HostId="", insertSelector="#qa", insertPlace="afterBegin"):
        if HostId == "":
            HostId = G.src.addon_name + "_host"
        innerHTML2 = innerHTML
        script = BeautifulSoup(f"""<script> 
        (()=>{{
         const Host = document.createElement("div");
         const root = Host.attachShadow({{mode:"open"}});
         const qa=document.body.querySelector("{insertSelector}")
         Host.id = "{HostId}";
         Host.style.zIndex = "999999";
         qa.insertAdjacentElement("{insertPlace}",Host)
         root.innerHTML=`{innerHTML2}`
         }})()
         </script>""", "html.parser")
        return script

    @staticmethod
    def LeftTopContainer_make(root: "BeautifulSoup"):
        """
            注意在这一层已经完成了,CSS注入
            传入的是从html文本解析成的beautifulSoup对象
            设计的是webview页面的左上角按钮,包括的内容有:
            anchorname            ->一切的开始
                style             ->样式设计
                div.container_L0  ->按钮所在地
                    div.header_L1 ->就是 hjp_bilink 这个名字所在的地方
                    div.body_L1   ->就是按钮和折叠栏所在的地方
            一开始会先检查这个anchorname元素是不是已经存在,如果存在则直接读取
            """
        # 寻找 anchorname ,建立 anchor_el,作为总的锚点.
        ID = G.addonName
        # ID = ""
        anchorname = ID if ID != "" else "anchor_container"
        resultli = root.select(f"#{anchorname}")
        if len(resultli) > 0:  # 如果已经存在,就直接取得并返回
            anchor_el: "element.Tag" = resultli[0]
        else:
            anchor_el: "element.Tag" = root.new_tag("div", attrs={"id": anchorname})
            root.insert(1, anchor_el)
            # 设计 style
            cfg = imports.Configs.Config.get()
            if cfg.anchor_style_text.value != "":
                style_str = cfg.anchor_style_text.value
            elif cfg.anchor_style_file.value != "" and os.path.exists(cfg.anchor_style_file.value):
                style_str = cfg.anchor_style_file.value
            else:
                style_str = open(G.src.path.anchor_CSS_file[cfg.anchor_style_preset.value], "r", encoding="utf-8").read()
            style = root.new_tag("style")
            style.string = style_str
            anchor_el.append(style)
            # 设计 容器 div.container_L0, div.header_L1和div.body_L1
            L0 = root.new_tag("div", attrs={"class": "container_L0"})
            header_L1 = root.new_tag("div", attrs={"class": "container_header_L1"})
            header_L1.string = G.addonName
            body_L1 = root.new_tag("div", attrs={"class": "container_body_L1"})
            L0.append(header_L1)
            L0.append(body_L1)
            anchor_el.append(L0)
        return anchor_el  # 已经传入了root,因此不必传出.

    # @staticmethod
    # def clipbox_exists(html, card_id=None):
    #     """任务:
    #     1检查clipbox的uuid是否在数据库中存在,如果存在,返回True,不存在返回False,
    #     2当存在时,检查卡片id是否是clipbox对应card_id,如果不是,则要添加,此卡片
    #     3搜索本卡片,得到clipbox的uuid,如果有搜到 uuid 但是又不在html解析出的uuid中, 则将数据库中的uuid的card_id删去本卡片的id
    #     """
    #     clipbox_uuid_li = HTML_clipbox_uuid_get(html)
    #     DB = G.DB
    #     DB.go(DB.table_clipbox)
    #     # print(clipbox_uuid_li)
    #     true_or_false_li = [DB.exists(DB.EQ(uuid=uuid)) for uuid in clipbox_uuid_li]
    #
    #     return (reduce(lambda x, y: x or y, true_or_false_li, False))

    @staticmethod
    def InTextButtonDeal(html_string):
        BackLinkReader = G.safe.in_text_admin.backlink_reader.BackLinkReader
        buttonli = BackLinkReader(html_str=html_string).backlink_get()
        if len(buttonli) > 0:
            finalstring = html_string[0:buttonli[0]["span"][0]]
            for i in range(len(buttonli) - 1):
                prevEnd, nextBegin = buttonli[i]["span"][1], buttonli[i + 1]["span"][0]
                finalstring += HTML.InTextButtonMake(buttonli[i]) + html_string[prevEnd:nextBegin]
            finalstring += HTML.InTextButtonMake(buttonli[-1]) + html_string[buttonli[-1]["span"][1]:]
        else:
            finalstring = html_string
        return finalstring

    @staticmethod
    def InTextButtonMake(data):

        card_id = data["card_id"]
        desc = data["desc"]
        h = BeautifulSoup("", "html.parser")
        b = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor intext button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        b.string = desc
        return b.__str__()
