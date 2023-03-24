# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = '$NAME.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/30 9:09'
"""
import logging
from urllib.parse import quote
# from math import ceil
from functools import reduce
from . import baseClass

from anki.cards import Card
from anki.notes import Note

from .language import rosetta
from .all_funcs.Gview import GviewOperation,GrapherOperation
from .all_funcs.Config import Config,GviewConfigOperation
from .all_funcs.Dialogs import Dialogs
from .all_funcs.card import CardOperation
from .all_funcs.browser import BrowserOperation
from .all_funcs.link import GlobalLinkDataOperation
from .all_widgets.widget_funcs import *
from .all_funcs.basic_funcs import *


译 = Translate
from .objs import LinkDataPair, LinkDataJSONInfo

if not ISLOCAL:
    pass
from .configsModel import ConfigModel, GViewData, GraphMode
from . import widgets

字典键名 = baseClass.枚举命名
枚举_视图结点类型 = baseClass.视图结点类型


def do_nothing(*args, **kwargs):
    pass


def write_to_log_file(s, need_timestamp=False):
    if G.ISDEBUG:
        f = open(G.src.path.logtext, "a", encoding="utf-8")
        f.write("\n" + ((datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "\n") if need_timestamp else "") + s)
        f.close()


def logger(logname=None, level=None, allhandler=None):
    if G.ISDEBUG:
        if logname is None:
            logname = "hjp_clipper"
        if level is None:
            level = logging.DEBUG
        printer = logging.getLogger(logname)
        printer.setLevel(level)
        log_dir = G.src.path.logtext

        fmt = "%(asctime)s %(levelname)s %(threadName)s  %(pathname)s\n%(filename)s " \
              "%(lineno)d\n%(funcName)s:\n %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt, datefmt)

        filehandle = logging.FileHandler(log_dir)
        filehandle.setLevel(level)
        filehandle.setFormatter(formatter)

        consolehandle = logging.StreamHandler()
        consolehandle.setLevel(level)
        consolehandle.setFormatter(formatter)
        printer.addHandler(consolehandle)
        printer.addHandler(filehandle)
        return printer
    else:
        return do_nothing




class MenuMaker:

    @staticmethod
    def gview_ankilink(menu, data):
        act = [Translate.文内链接, Translate.html链接, Translate.markdown链接, Translate.orgmode链接]
        # f = [lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.inAnki, data),
        #      lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.html, data),
        #      lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.markdown, data),
        #      lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.orgmode, data), ]
        f = [
                lambda: AnkiLinksCopy2.Open.Gview.from_htmlbutton(data),
                lambda: AnkiLinksCopy2.Open.Gview.from_htmllink(data),
                lambda: AnkiLinksCopy2.Open.Gview.from_md(data),
                lambda: AnkiLinksCopy2.Open.Gview.from_orgmode(data)
        ]
        list(map(lambda x: menu.addAction(act[x]).triggered.connect(f[x]), range(len(f))))
        return menu


class IntroductionOperation:
    pass




class CardTemplateOperation:
    @staticmethod
    def GetModelFromId(Id: int):
        if G.ISLOCALDEBUG:
            return None
        return mw.col.models.get(Id)

    @staticmethod
    def GetNameFromId(Id: int):
        return CardTemplateOperation.GetModelFromId(Id)[""]

    @staticmethod
    def GetAllTemplates():
        if G.ISLOCALDEBUG:
            return []
        return mw.col.models.all()


class Compatible:

    @staticmethod
    def CardId():
        if pointVersion() < 45:
            CardId = NewType("CardId", int)
            return CardId
        else:
            from anki.cards import CardId
            return CardId

    @staticmethod
    def NoteId():
        if pointVersion() < 45:
            NoteId = NewType("NoteId", int)
            return NoteId
        else:
            from anki.notes import NoteId
            return NoteId

    @staticmethod
    def DeckId():
        if pointVersion() < 45:
            DeckId = NewType("DeckId", int)
            return DeckId
        else:
            from anki.decks import DeckId
            return DeckId

    @staticmethod
    def BrowserPreviewer():
        if pointVersion() < 45:
            DeckId = NewType("DeckId", int)
            return DeckId
        else:
            from anki.decks import DeckId
            return DeckId


class ReviewerOperation:
    @staticmethod
    def time_up_buzzer(card: "Card", starttime):
        def buzzer(starttime, card: "Card"):
            if starttime == G.cardChangedTime and mw.state == "review" and card.id == mw.reviewer.card.id:
                if Config.get().time_up_skip_click.value:
                    ReviewerOperation.time_up_auto_action(card)
                    tooltip(f"{Config.get().time_up_buzzer.value} {rosetta('秒')} {rosetta('时间到')}")
                    return
                d = widgets.message_box_for_time_up(Config.get().time_up_buzzer.value)
                if d == Translate.默认操作:
                    ReviewerOperation.time_up_auto_action(card)
                    return
                elif d == Translate.重新计时:
                    starttime = G.cardChangedTime = time.time()
                    timegap = Config.get().time_up_buzzer.value
                    QTimer.singleShot(timegap * 1000, lambda: buzzer(starttime, card))
                else:
                    return

        timegap = Config.get().time_up_buzzer.value
        QTimer.singleShot(timegap * 1000, lambda: buzzer(starttime, card))

    @staticmethod
    def time_up_auto_action(card: "Card"):
        def pick_date():
            value, ok = QInputDialog.getInt(None, "time_up_auto_action", "请输入推迟天数", 0)
            if not ok:
                value = 0
            return value
            pass

        actcode = Config.get().time_up_auto_action.value
        if actcode == 0: return
        actions = {}
        list(map(lambda k: actions.__setitem__(k, lambda card: CardOperation.answer_card(card, k)), range(1, 5)))
        list(map(lambda kv: actions.__setitem__(kv[1], lambda card: CardOperation.delay_card(card, kv[1])), [(5, 1), (6, 3), (7, 7), (8, 30)]))
        actions[9] = lambda _card: CardOperation.delay_card(_card, pick_date())
        actions[10] = lambda _card: mw.reviewer._showAnswer()
        actions[actcode](card)

    @staticmethod
    def refresh():
        pass



class EditorOperation:
    @staticmethod
    def make_PDFlink(editor: "Editor"):
        """复制文件路径,或者file协议链接,或者打开对话框后再粘贴"""
        # TODO 无法在reviewer点击编辑时,提供右键弹出菜单入口
        # TODO 同上,无法在新建卡片中显示

        clipboard = QApplication.clipboard()
        text = clipboard.text()

        dialog = widgets.Dialog_PDFUrlTool()
        dialog.widgets[Translate.pdf路径].setText(text)
        dialog.widgets[Translate.pdf默认显示页码].setChecked(Config.get().PDFLink_show_pagenum.value)
        config = PDFLink.GetPathInfoFromPreset(text)
        if config is not None:
            dialog.widgets[Translate.pdf名字].setText(config[1])
            dialog.widgets[Translate.pdf默认显示页码].setChecked(config[3])
            dialog.widgets[Translate.pdf样式].setText(config[2])

        dialog.exec()
        # if dialog.needpaste:tooltip("neeapaste")
        if dialog.needpaste: editor.onPaste()
        return text


class CustomProtocol:
    # 自定义url协议,其他的都是固定的,需要获取anki的安装路径

    @staticmethod
    def set():
        root = QSettings("HKEY_CLASSES_ROOT", QSettings.Format.NativeFormat)
        root.beginGroup("ankilink")
        root.setValue("Default", "URL:Ankilink")
        root.setValue("URL Protocol", "")
        root.endGroup()
        command = QSettings(r"HKEY_CLASSES_ROOT\anki.ankiaddon\shell\open\command", QSettings.Format.NativeFormat)
        shell_open_command = QSettings(r"HKEY_CLASSES_ROOT\ankilink\shell\open\command", QSettings.Format.NativeFormat)
        shell_open_command.setValue(r"Default", command.value("Default"))

    @staticmethod
    def exists():
        setting = QSettings(r"HKEY_CLASSES_ROOT\ankilink", QSettings.Format.NativeFormat)
        return len(setting.childGroups()) > 0




class Media:
    """"""

    # @staticmethod
    # def clipbox_png_save(clipuuid):
    #     if platform.system() in {"Darwin", "Linux"}:
    #         tooltip("当前系统暂时不支持该功能")
    #         return
    #     else:
    #         from ..clipper2.exports import fitz
    #     if ISLOCALDEBUG:
    #         mediafolder = r"D:\png"
    #     else:
    #         mediafolder = os.path.join(mw.pm.profileFolder(), "collection.media")
    #     DB = G.DB
    #     clipbox_ = DB.go(DB.table_clipbox).select(uuid=clipuuid).return_all().zip_up()[0]
    #     clipbox = G.objs.ClipboxRecord(**clipbox_)
    #     pdfinfo_ = DB.go(DB.table_pdfinfo).select(uuid=clipbox.pdfuuid).return_all().zip_up()[0]
    #     pdfinfo = G.objs.PDFinfoRecord(**pdfinfo_)
    #     doc: "fitz.Document" = fitz.open(pdfinfo.pdf_path)
    #     # 0.144295302 0.567695962 0.5033557047 0.1187648456
    #     page = doc.load_page(clipbox.pagenum)
    #     pagerect: "fitz.rect_like" = page.rect
    #     x0, y0 = clipbox.x * pagerect.width, clipbox.y * pagerect.height
    #     x1, y1 = x0 + clipbox.w * pagerect.width, y0 + clipbox.h * pagerect.height
    #     pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2),
    #                              clip=fitz.Rect(x0, y0, x1, y1))
    #     pngdir = os.path.join(mediafolder, f"""hjp_clipper_{clipbox.uuid}_.png""")
    #     write_to_log_file(pngdir + "\n" + f"w={pixmap.width} h={pixmap.height}")
    #     if os.path.exists(pngdir):
    #         # showInfo("截图已更新")
    #         os.remove(pngdir)
    #     pixmap.save(pngdir)


class LinkPoolOperation:
    """针对链接池设计"""

    class M:
        """各种状态选择"""
        before_clean = 0
        directly = 1
        by_group = 2
        complete_map = 3
        group_by_group = 4
        unlink_by_path = 5
        unlink_by_node = 6

    @staticmethod
    def both_refresh(*args):
        """0,1,2 可选刷新"""
        if ISLOCALDEBUG:
            return
        o = [CardOperation, BrowserOperation, GrapherOperation]
        if len(args) > 0:
            for i in args:
                o[i].refresh()
        else:
            for Op in o:
                Op.refresh()

    @staticmethod
    def get_template():
        d = {"IdDescPairs": [], "addTag": ""}
        return d

    @staticmethod
    def read():
        d = json.load(open(G.src.path.linkpool_file, "r", encoding="utf-8"))
        x = G.objs.LinkPoolModel(fromjson=d)
        return x

    @staticmethod
    def insert(pair_li: "list[G.objs.LinkDataPair]" = None, mode=1, need_show=True, FROM=None):
        if FROM == DataFROM.shortCut:
            pair_li = BrowserOperation.get_selected_card()
            if len(pair_li) == 0:
                tooltip(Translate.请选择卡片)
                return
            mode = Config.get().default_insert_mode.value
        L = LinkPoolOperation
        if mode == L.M.before_clean:
            L.clear()
            d = L.read()
            d.IdDescPairs = [[pair] for pair in pair_li]
        elif mode == L.M.directly:
            d = L.read()
            d.IdDescPairs += [[pair] for pair in pair_li]
        elif mode == L.M.by_group:
            d = L.read()
            d.IdDescPairs += [[pair for pair in pair_li]]
        else:
            raise TypeError("不支持的操作")
        L.write(d.todict())
        from ..bilink.dialogs.linkpool import LinkPoolDialog
        if need_show:
            if isinstance(G.mw_linkpool_window, LinkPoolDialog):
                G.mw_linkpool_window.activateWindow()
            else:
                G.mw_linkpool_window = LinkPoolDialog()
                G.mw_linkpool_window.show()

    @staticmethod
    def clear():
        d = LinkPoolOperation.get_template()
        LinkPoolOperation.write(d)
        return LinkPoolOperation

    @staticmethod
    def write(d: "dict"):
        json.dump(d, open(G.src.path.linkpool_file, "w", encoding="utf-8"))
        return LinkPoolOperation

    @staticmethod
    def exists():
        return os.path.exists(G.src.path.linkpool_file)

    @staticmethod
    def link(mode=4, pair_li: "Optional[list[G.objs.LinkDataPair]]" = None, FROM=None):
        if FROM == DataFROM.shortCut:
            pair_li = BrowserOperation.get_selected_card()
            if len(pair_li) == 0:
                tooltip(Translate.请选择卡片)
                return
            mode = Config.get().default_link_mode.value

        def on_quit_handle(timestamp):
            cfg = Config.get()
            if cfg.open_browser_after_link.value == 1:
                if cfg.add_link_tag.value == 1:
                    BrowserOperation.search(f"""tag:hjp-bilink::timestamp::{timestamp}""").activateWindow()
                else:
                    s = ""
                    for pair in pair_li:
                        s += f"cid:{pair.card_id} or "
                    BrowserOperation.search(s[0:-4]).activateWindow()
            G.mw_progresser.close()
            G.mw_universal_worker.allevent.unbind()
            LinkPoolOperation.both_refresh()

        from . import widgets
        if pair_li is not None:
            LinkPoolOperation.insert(pair_li, mode=LinkPoolOperation.M.before_clean, need_show=False)
        G.mw_progresser = widgets.UniversalProgresser()  # 实例化一个进度条
        G.mw_universal_worker = LinkPoolOperation.LinkWorker(mode=mode)  # 实例化一个子线程
        G.mw_universal_worker.allevent = G.objs.AllEventAdmin([  # 给子线程的不同情况提供回调函数
                [G.mw_universal_worker.on_quit, on_quit_handle],  # 完成时回调
                [G.mw_universal_worker.on_progress, G.mw_progresser.value_set],  # 进度回调
        ]).bind()
        G.mw_universal_worker.start()

    @staticmethod
    def unlink(mode=6, pair_li: "Optional[list[G.objs.LinkDataPair]]" = None, FROM=None):
        if FROM == DataFROM.shortCut:
            pair_li = BrowserOperation.get_selected_card()
            if len(pair_li) == 0:
                tooltip(Translate.请选择卡片)
                return
            mode = Config.get().default_unlink_mode.value
        LinkPoolOperation.link(mode=mode, pair_li=pair_li)

    class LinkWorker(QThread):
        on_progress = pyqtSignal(object)
        on_quit = pyqtSignal(object)

        def __init__(self, mode=3):
            super().__init__()

            self.waitting = False
            self.timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            self.allevent: 'Optional[G.objs.AllEventAdmin]' = None
            self.timegap = 0.1
            self.mode = mode

        def run(self):
            L = LinkPoolOperation
            d = L.read()
            cfg = Config.get()
            linkdatali = d.tolinkdata()
            flatten: "list[LinkDataJSONInfo]" = reduce(lambda x, y: x + y, linkdatali, [])
            total, count = len(flatten), 0
            DB = G.DB
            # 先加tag

            for pair in flatten:
                pair.add_tag(d.addTag)
                if cfg.add_link_tag.value:
                    pair.add_timestamp_tag(self.timestamp)
                count += 1
                self.on_progress.emit(Utils.percent_calc(total, count, 0, 25))

            # 根据不同的模式进行不同的操作
            if self.mode in {L.M.complete_map, L.M.unlink_by_node}:
                total, count = len(flatten), 0
                for linkinfoA in flatten:
                    total2, count2 = len(flatten), 0
                    for linkinfoB in flatten:
                        if linkinfoB.self_data.card_id != linkinfoA.self_data.card_id:
                            if self.mode == L.M.complete_map:
                                GlobalLinkDataOperation.bind(linkinfoA, linkinfoB, needsave=False)
                            elif self.mode == L.M.unlink_by_node:
                                GlobalLinkDataOperation.unbind(linkinfoA, linkinfoB, needsave=False)
                        count2 += 1
                        self.on_progress.emit(Utils.percent_calc(total, (count2 / total2 + count), 25, 50))
                    count += 1
            elif self.mode in (L.M.group_by_group, L.M.unlink_by_path):
                total, count = len(linkdatali), 0
                r = self.reducer(count, total, self, d)
                reduce(r.reduce_link, linkdatali)
            total, count = len(flatten), 0
            DB.go(DB.table_linkinfo)
            for linkinfo in flatten:
                # temp = linkinfo.to_DB_record
                linkinfo.save_to_DB()
                # card_id, data = temp["card_id"], temp["data"]
                # DB.replace(card_id=card_id, data=data).commit(need_commit=False)
                count += 1
                self.on_progress.emit(Utils.percent_calc(total, count, 75, 25))

            self.on_quit.emit(self.timestamp)

        class reducer:
            def __init__(self, count, total, worker: "LinkPoolOperation.LinkWorker", d):
                from ..bilink import linkdata_admin
                self.count = count
                self.total = total
                self.worker = worker
                self.d = d
                self.linkdata_admin: "" = linkdata_admin

            def reduce_link(self, groupA: "list[G.objs.LinkDataJSONInfo]", groupB: "list[G.objs.LinkDataJSONInfo]"):
                self.worker.on_progress.emit(Utils.percent_calc(self.total, self.count, 25, 50))
                L = LinkPoolOperation
                for linkinfoA in groupA:
                    for linkinfoB in groupB:
                        if self.worker.mode == L.M.group_by_group:
                            GlobalLinkDataOperation.bind(linkinfoA, linkinfoB, needsave=False)
                        elif self.worker.mode == L.M.unlink_by_path:
                            GlobalLinkDataOperation.unbind(linkinfoA, linkinfoB, needsave=False)
                self.count += 1
                return groupB


class 卡片模板操作:
    @staticmethod
    def 获取模板名(模板编号, 缺省值: "str" = None):
        if 模板编号 > 0:
            return mw.col.models.get(模板编号)["name"]
        else:
            return 缺省值


class 牌组操作:
    @staticmethod
    def 获取牌组名(模板编号, 缺省值: "str" = None):
        if 模板编号 > 0:
            return mw.col.decks.name(模板编号)
        else:
            return 缺省值


class 卡片字段操作:
    @staticmethod
    def 获取字段名(模板编号, 字段编号, 缺省值: "str" = None):
        字段名列表 = []
        if 模板编号 > 0:
            模板 = mw.col.models.get(模板编号)
            字段名列表 = mw.col.models.field_names(模板)
            if len(字段名列表) > 字段编号 >= 0:
                return 字段名列表[字段编号]
            else:
                return 缺省值
        else:
            return 缺省值


class ModelOperation:
    @staticmethod
    def get_all():
        data = []
        if ISLOCALDEBUG:
            data = [{"id": 123456, "name": "hello"}]
            return data
        model = mw.col.models.all_names_and_ids()
        for i in model:
            data.append({"id": i.id, "name": i.name})
        return data


class DeckOperation:
    @staticmethod
    def get_all():
        data = []
        if ISLOCALDEBUG:
            data = [{"id": 123456, "name": "hello"}]
            return data

        deck = mw.col.decks.all_names_and_ids()
        for i in deck:
            data.append({"id": i.id, "name": i.name})
        return data


class MonkeyPatch:

    @staticmethod
    def AddCards_closeEvent(funcs):
        from aqt.addcards import AddCards
        def 包装器(self: "AddCards", evt: "QCloseEvent"):
            G.常量_当前等待新增卡片的视图索引 = None
            funcs(self, evt)
            pass

        return 包装器
        pass

    @staticmethod
    def mw_closeevent(funcs):
        def wrapper(*args, **kwargs):
            self = args[0]
            event = args[1]
            showInfo("hi!")
            funcs(self, event)

        return wrapper

    @staticmethod
    def Reviewer_nextCard(funcs):
        def wrapper(self: "Reviewer"):
            funcs(self)
            cfg = Config.get()
            if cfg.too_fast_warn.value:
                G.nextCard_interval.append(int(datetime.datetime.now().timestamp() * 1000))
                threshold = cfg.too_fast_warn_everycard.value
                tooltip(G.nextCard_interval.__str__())
                if len(G.nextCard_interval) > 1:  # 大于1才有阈值讨论的余地
                    last = G.nextCard_interval[-2]
                    now = G.nextCard_interval[-1]
                    # tooltip(str(now-last))
                    if now - last > cfg.too_fast_warn_interval.value:
                        G.nextCard_interval.clear()
                        return
                    else:
                        if len(G.nextCard_interval) >= threshold:
                            showInfo(Translate.过快提示)
                            G.nextCard_interval.clear()

        return wrapper

    @staticmethod
    def Reviewer_showEaseButtons(funcs):
        def freezeAnswerCard(self: Reviewer):
            _answerCard = self._answerCard
            self._answerCard = lambda x: tooltip(Translate.已冻结)
            return _answerCard

        def recoverAnswerCard(self: Reviewer, _answerCard):
            self._answerCard = _answerCard

        def _showEaseButtons(self: Reviewer):
            funcs(self)
            cfg = Config.get()
            if cfg.freeze_review.value:
                interval = cfg.freeze_review_interval.value
                self.bottom.web.eval("""
                buttons = document.querySelectorAll("button[data-ease]")
                buttons.forEach(button=>{button.setAttribute("disabled",true)})
                setTimeout(()=>{buttons.forEach(button=>button.removeAttribute("disabled"))},
                """ + str(interval) + """)""")

                self.mw.blockSignals(True)
                tooltip(Translate.已冻结)
                _answerCard = freezeAnswerCard(self)
                QTimer.singleShot(interval, lambda: recoverAnswerCard(self, _answerCard))
                QTimer.singleShot(interval, lambda: tooltip(Translate.已解冻))

        return _showEaseButtons

    @staticmethod
    def BrowserSetupMenus(funcs, after, *args, **kwargs):
        def setupMenus(self: "Browser"):
            funcs(self)
            after(self, *args, **kwargs)

        return setupMenus

    @staticmethod
    def onAppMsgWrapper(self: "AnkiQt"):
        # self.app.appMsg.connect(self.onAppMsg)
        """"""

        def handle_AnkiLink(buf):
            # buf加了绝对路径,所以要去掉
            # 有时候需要判断一下
            tooltip(buf)

            def handle_opencard(id):
                if CardOperation.exists(id):
                    Dialogs.open_custom_cardwindow(id).activateWindow()
                else:
                    tooltip("card not found")
                pass

            def handle_openbrowser(search):
                BrowserOperation.search(search).activateWindow()
                pass

            def handle_opengview(uuid):
                if GviewOperation.exists(uuid=uuid):
                    data = GviewOperation.load(uuid=uuid)
                    Dialogs.open_grapher(gviewdata=data, mode=GraphMode.view_mode)
                else:
                    tooltip("view not found")

            from .objs import CmdArgs
            ankilink = G.src.ankilink
            # Utils.LOG.file_write(buf, True)
            cmd_dict = {
                    # 下面的是1版命令格式
                    f"{ankilink.Cmd.opencard}"                           : handle_opencard,
                    f"{ankilink.Cmd.openbrowser_search}"                 : handle_openbrowser,
                    f"{ankilink.Cmd.opengview}"                          : handle_opengview,
                    # 下面的是2版命令格式
                    f"{ankilink.Cmd.open}?{ankilink.Key.card}"           : handle_opencard,
                    f"{ankilink.Cmd.open}?{ankilink.Key.gview}"          : handle_opengview,
                    f"{ankilink.Cmd.open}?{ankilink.Key.browser_search}" : handle_openbrowser,
                    # ANKI关闭时的模式
                    f"{ankilink.Cmd.open}/?{ankilink.Key.card}"          : handle_opencard,
                    f"{ankilink.Cmd.open}/?{ankilink.Key.gview}"         : handle_opengview,
                    f"{ankilink.Cmd.open}/?{ankilink.Key.browser_search}": handle_openbrowser,
            }

            if buf.startswith(f"{G.src.ankilink.protocol}://"):  # 此时说明刚打开就进来了,没有经过包装,格式取buf[11:-1]
                cmd = CmdArgs(buf[11:].split("="))
            else:
                cmd = CmdArgs(buf.split(f"{G.src.ankilink.protocol}:\\")[-1].replace("\\", "").split("="))

            if cmd.type in cmd_dict:
                # showInfo(cmd.args)
                cmd_dict[cmd.type](cmd.args)

            else:
                showInfo("打开状态下, 未知指令/unknown command:  <br>" + cmd.type)
            pass

        def onAppMsg(buf: str):
            is_addon = self._isAddon(buf)
            is_link = "ANKILINK:" in buf.upper()
            if self.state == "startup":
                # try again in a second
                self.progress.timer(
                        1000, lambda: self.onAppMsg(buf), False, requiresCollection=False
                )
                return
            elif self.state == "profileManager":
                # can't raise window while in profile manager
                if buf == "raise":
                    return None
                self.pendingImport = buf
                if is_addon:
                    msg = tr.qt_misc_addon_will_be_installed_when_a()
                elif is_link:
                    msg = "在profile窗口下,ankilink功能无法正常使用"
                else:
                    msg = tr.qt_misc_deck_will_be_imported_when_a()
                tooltip(msg)
                return
            if not self.interactiveState() or self.progress.busy():
                # we can't raise the main window while in profile dialog, syncing, etc
                if buf != "raise":
                    showInfo(
                            tr.qt_misc_please_ensure_a_profile_is_open(),
                            parent=None,
                    )
                return None
            # raise window
            if isWin:
                # on windows we can raise the window by minimizing and restoring
                self.showMinimized()
                self.setWindowState(Qt.WindowActive)
                self.showNormal()
            else:
                # on osx we can raise the window. on unity the icon in the tray will just flash.
                self.activateWindow()
                self.raise_()
            if buf == "raise":
                return None

            # import / add-on installation
            if is_addon:
                self.installAddon(buf)
            elif is_link:
                handle_AnkiLink(buf)
            else:
                self.handleImport(buf)

            return None

        return onAppMsg

    if not ISLOCALDEBUG:
        class BrowserPreviewer(MultiCardPreviewer):
            _last_card_id = 0
            _parent: Optional["Browser"]

            def __init__(
                    self, parent: "Browser", mw: "AnkiQt", on_close: Callable[[], None]
            ) -> None:
                super().__init__(parent=parent, mw=mw, on_close=on_close)
                self.bottom_layout = QGridLayout()
                self.bottom_layout_all = QGridLayout()
                self.reviewWidget = widgets.ReviewButtonForCardPreviewer(self, self.bottom_layout_all)

            def card(self) -> Optional[Card]:
                if self._parent.singleCard:
                    return self._parent.card
                else:
                    return None

            def render_card(self) -> None:
                super().render_card()

            def _create_gui(self):
                super()._create_gui()
                self.vbox.removeWidget(self.bbox)
                self.bottom_layout_all.addWidget(self.bbox, 0, 1, 1, 1)
                self.vbox.addLayout(self.bottom_layout_all)

            def card_changed(self) -> bool:
                c = self.card()
                if not c:
                    return True
                else:
                    changed = c.id != self._last_card_id
                    self._last_card_id = c.id
                    return changed

            def _on_prev_card(self) -> None:
                self._parent.onPreviousCard()

            def _on_next_card(self) -> None:
                self._parent.onNextCard()

            def _should_enable_prev(self) -> bool:
                return super()._should_enable_prev() or self._parent.has_previous_card()

            def _should_enable_next(self) -> bool:
                return super()._should_enable_next() or self._parent.has_next_card()

            def _render_scheduled(self) -> None:
                super()._render_scheduled()
                self._updateButtons()

            def _on_prev(self) -> None:

                if self._state == "answer" and not self._show_both_sides:
                    self._state = "question"
                    self.render_card()
                else:
                    self._on_prev_card()
                QTimer.singleShot(100, lambda: self.reviewWidget.update_info())

            def _on_next(self) -> None:
                if self._state == "question":
                    self._state = "answer"
                    self.render_card()
                else:
                    self._on_next_card()
                QTimer.singleShot(100, lambda: self.reviewWidget.update_info())

    else:
        class BrowserPreviewer:
            def __init__(self):
                raise Exception("not support in this env")




class AnchorOperation:
    @staticmethod
    def if_empty_then_remove(html_str: "str"):
        bs = BeautifulSoup(html_str, "html.parser")
        roots = bs.select(f"#{G.addonName}")
        tags = bs.select(f"#{G.addonName} .container_body_L1")
        if len(roots) > 0:
            root: "BeautifulSoup" = roots[0]
        else:
            return bs.__str__()
        if len(tags) > 0 and len(list(tags[0].childGenerator())) == 0:
            root.extract()
        return bs.__str__()



def button_icon_clicked_switch(button: QToolButton, old: list, new: list, callback: "callable" = None):
    if button.text() == old[0]:
        button.setText(new[0])
        button.setIcon(QIcon(new[1]))
    else:
        button.setText(old[0])
        button.setIcon(QIcon(old[1]))
    if callback:
        callback(button.text())


def str_shorten(string, length=30) -> str:
    if len(string) <= length:
        return string
    else:
        return string[0:int(length / 2) - 3] + "..." + string[-int(length / 2):]


def HTML_injecttoweb(htmltext, card, kind):
    """在web渲染前,注入html代码,"""
    if kind in [
            "previewQuestion",
            "previewAnswer",
            "reviewQuestion",
            "reviewAnswer"
    ]:
        from lib.common_tools.all_funcs.HTMLbutton_render import HTMLbutton_make
        html_string = HTMLbutton_make(htmltext, card)

        return html_string
    else:
        return htmltext


def HTML_clipbox_sync_check(card_id, root):
    # 用于保持同步
    assert type(root) == BeautifulSoup
    assert type(card_id) == str
    DB = G.DB
    clipbox_from_DB_ = DB.go(DB.table_clipbox).select(DB.LIKE("card_id", card_id)).return_all().zip_up()
    clipbox_from_DB = set([clipbox["uuid"] for clipbox in clipbox_from_DB_])
    # 选取 clipbox from field
    fields = "\n".join(mw.col.getCard(CardId(int(card_id))).note().fields)
    clipbox_from_field = set(HTML_clipbox_uuid_get(fields))
    # 多退少补,
    DBadd = clipbox_from_field - clipbox_from_DB
    DBdel = clipbox_from_DB - clipbox_from_field
    # print(
    #     f"card_id={card_id},clipbox_from_DB={clipbox_from_DB}, clipbox_from_field={clipbox_from_field}, DBADD={DBadd}.  DBdel={DBdel}")
    if len(DBadd) > 0:
        # DB.add_card_id(DB.where_maker(IN=True, colname="uuid", vals=DBadd), card_id)
        DB.add_card_id(DB.IN("uuid", *DBadd), card_id)
    if len(DBdel) > 0:
        # DB.del_card_id(DB.where_maker(IN=True, colname="uuid", vals=DBdel), card_id)
        DB.del_card_id(DB.IN("uuid", *DBdel), card_id)
    DB.end()
    pass


def HTML_clipbox_PDF_info_dict_read(root):
    """ 从所给的HTML 中读取 每个clipbox对应的 PDFuuid,以及其名字,和所包含的页码"""
    assert type(root) == BeautifulSoup
    clipbox_from_field = set(HTML_clipbox_uuid_get(root))
    DB = G.DB
    DB.go(DB.table_clipbox).select(DB.IN("uuid", *clipbox_from_field))

    # DB.go(DB.table_clipbox).select(where=DB.where_maker(IN=True, vals=clipbox_from_field, colname="uuid"))
    # print(DB.excute_queue[-1])
    record_li = DB.return_all().zip_up().to_clipbox_data()
    PDF_info_dict = {}  # {uuid:{pagenum:{},pdfname:""}}
    for record in record_li:
        PDFinfo = DB.go(DB.table_pdfinfo).select(uuid=record.pdfuuid).return_all().zip_up()[0].to_pdfinfo_data()
        if PDFinfo.uuid not in PDF_info_dict:
            PDF_info_dict[PDFinfo.uuid] = {"pagenum": set(),  # 页码唯一化
                                           "info"   : PDFinfo}  # 只提取页码, 大小重新再设定.偏移量也重新设定.
        PDF_info_dict[PDFinfo.uuid]["pagenum"].add(record.pagenum)

    return PDF_info_dict


def HTML_LeftTopContainer_detail_el_make(root: "BeautifulSoup", summaryname, attr: "dict" = None):
    """这是一个公共的步骤,设计一个details, root 传进来无所谓的, 不会基于他做操作,只是引用了他的基本功能
    details.hjp_bilink .details
        summary
        div
    """
    if attr is None:
        attr = {}
    attrs = attr.copy()
    if "class" in attrs:
        attrs["class"] += " hjp_bilink details"
    else:
        attrs["class"] = "hjp_bilink details"
    # print(attrs)
    details = root.new_tag("details", attrs=attrs)
    summary = root.new_tag("summary")
    summary.string = summaryname
    div = root.new_tag("div")
    details.append(summary)
    details.append(div)
    return details, div


def HTML_clipbox_uuid_get(html):
    if type(html) == str:
        root = BeautifulSoup(html, "html.parser")
    elif type(html) == BeautifulSoup:
        root = html
    else:
        raise TypeError("无法处理参数类型: {}".format(type(html)))
    imgli = root.find_all("img", src=re.compile("hjp_clipper_\w{8}_.png"))
    clipbox_uuid_li = [re.sub("hjp_clipper_(\w+)_.png", lambda x: x.group(1), img.attrs["src"]) for img in imgli]
    return clipbox_uuid_li


def HTML_clipbox_exists(html, card_id=None):
    """任务:
    1检查clipbox的uuid是否在数据库中存在,如果存在,返回True,不存在返回False,
    2当存在时,检查卡片id是否是clipbox对应card_id,如果不是,则要添加,此卡片
    3搜索本卡片,得到clipbox的uuid,如果有搜到 uuid 但是又不在html解析出的uuid中, 则将数据库中的uuid的card_id删去本卡片的id
    """
    clipbox_uuid_li = HTML_clipbox_uuid_get(html)
    DB = G.DB
    DB.go(DB.table_clipbox)
    # print(clipbox_uuid_li)
    true_or_false_li = [DB.exists(DB.EQ(uuid=uuid)) for uuid in clipbox_uuid_li]
    DB.end()
    return (reduce(lambda x, y: x or y, true_or_false_li, False))


def HTML_LeftTopContainer_make(root: "BeautifulSoup"):
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
        cfg = Config.get()
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


@dataclasses.dataclass
class DataFROM:
    shortCut = 0


class AnkiLinksCopy2:
    """新版的链接
    格式f: {ankilink}://command?key=value
    警告: 这个版本无法正常运行
    """
    protocol = f"{G.src.ankilink.protocol}"

    class Open:
        command = G.src.ankilink.cmd.open

        class Card:
            """"""
            key = G.src.ankilink.Key.card

            @staticmethod
            def from_htmllink(pairs_li: 'list[G.objs.LinkDataPair]'):
                """"""
                AnkiLinksCopy2.Open.Card._gen_link(pairs_li, AnkiLinksCopy2.LinkType.htmllink)

            @staticmethod
            def from_htmlbutton(pairs_li: 'list[G.objs.LinkDataPair]'):
                AnkiLinksCopy2.Open.Card._gen_link(pairs_li, AnkiLinksCopy2.LinkType.htmlbutton)

            @staticmethod
            def from_markdown(pairs_li: 'list[G.objs.LinkDataPair]'):
                AnkiLinksCopy2.Open.Card._gen_link(pairs_li, AnkiLinksCopy2.LinkType.markdown)

            @staticmethod
            def from_orgmode(pairs_li: 'list[G.objs.LinkDataPair]'):
                AnkiLinksCopy2.Open.Card._gen_link(pairs_li, AnkiLinksCopy2.LinkType.orgmode)

            @staticmethod
            def _gen_link(pairs_li: 'list[G.objs.LinkDataPair]', mode):
                clipboard = QApplication.clipboard()
                mmdata = QMimeData()
                A = AnkiLinksCopy2
                B = AnkiLinksCopy2.Open
                C = AnkiLinksCopy2.Open.Card
                header = f"{A.protocol}://{B.command}?{C.key}="
                puretext = ""
                total = ""
                if mode == A.LinkType.htmllink:
                    for pair in pairs_li:
                        total += f"""<a href="{header}{pair.card_id}">{pair.desc}<a><br>""" + "\n"
                        puretext += f"""{header}{pair.card_id}\n"""
                    mmdata.setHtml(total)
                    mmdata.setText(puretext)
                    clipboard.setMimeData(mmdata)
                    tooltip(puretext)
                    return
                elif mode == A.LinkType.htmlbutton:
                    def buttonmaker(p: LinkDataPair):
                        return f"""<div >|<button class="hjp_bilink ankilink button" onclick="javascript:pycmd('{header}{p.card_id}');">{p.desc}</button>|</div>"""

                    for pair in pairs_li:
                        total += buttonmaker(pair)
                    clipboard.setText(total)
                elif mode == A.LinkType.markdown:
                    for pair in pairs_li:
                        total += f"""[{pair.desc}]({header}{pair.card_id})\n"""
                    clipboard.setText(total)
                elif mode == A.LinkType.orgmode:
                    for pair in pairs_li:
                        total += f"""[[{header}{pair.card_id}][{pair.desc}]]\n"""
                    clipboard.setText(total)
                tooltip(total)

        class BrowserSearch:
            """"""
            key = G.src.ankilink.Key.browser_search

            @staticmethod
            def from_htmllink(browser: "Browser"):
                """"""
                AnkiLinksCopy2.Open.BrowserSearch._gen_link(browser, AnkiLinksCopy2.LinkType.htmllink)

            # @staticmethod
            # def from_htmlbutton(browser: "Browser"):
            #     """"""
            #     AnkiLinksCopy2.Open.BrowserSearch.gen_link(browser, AnkiLinksCopy2.LinkType.htmlbutton)

            @staticmethod
            def from_md(browser: "Browser"):
                """"""
                AnkiLinksCopy2.Open.BrowserSearch._gen_link(browser, AnkiLinksCopy2.LinkType.markdown)

            @staticmethod
            def from_orgmode(browser: "Browser"):
                """"""
                AnkiLinksCopy2.Open.BrowserSearch._gen_link(browser, AnkiLinksCopy2.LinkType.orgmode)

            @staticmethod
            def _gen_link(browser: "Browser", mode):
                """"""
                mmdata = QMimeData()
                clipboard = QApplication.clipboard()
                A = AnkiLinksCopy2
                B = AnkiLinksCopy2.Open
                C = AnkiLinksCopy2.Open.BrowserSearch
                searchstring = browser.form.searchEdit.currentText()
                tooltip(searchstring)
                header = f"{A.protocol}://{B.command}?{C.key}="
                href = header + quote(searchstring)

                func_dict = {
                        A.LinkType.htmllink: lambda: f"""<a href="{href}">{Translate.Anki搜索}:{searchstring}</a>""",

                        A.LinkType.orgmode : lambda: f"[[{href}][{Translate.Anki搜索}:{searchstring}]]",
                        A.LinkType.markdown: lambda: f"[{Translate.Anki搜索}:{searchstring}]({href})",
                }
                if mode == A.LinkType.htmllink:
                    mmdata.setText(href)
                    mmdata.setHtml(func_dict[mode]())
                    clipboard.setMimeData(mmdata)
                else:
                    clipboard.setText(func_dict[mode]())
                tooltip(href)

        class Gview:
            """"""
            key = G.src.ankilink.Key.gview

            @staticmethod
            def from_htmllink(data: "GViewData"):
                """"""
                AnkiLinksCopy2.Open.Gview._gen_link(data, AnkiLinksCopy2.LinkType.htmllink)

            @staticmethod
            def from_htmlbutton(data: "GViewData"):
                """"""
                AnkiLinksCopy2.Open.Gview._gen_link(data, AnkiLinksCopy2.LinkType.htmlbutton)

            @staticmethod
            def from_md(data: "GViewData"):
                """"""
                AnkiLinksCopy2.Open.Gview._gen_link(data, AnkiLinksCopy2.LinkType.markdown)

            @staticmethod
            def from_orgmode(data: "GViewData"):
                """"""
                AnkiLinksCopy2.Open.Gview._gen_link(data, AnkiLinksCopy2.LinkType.orgmode)

            @staticmethod
            def _gen_link(data: "GViewData", mode):
                mmdata = QMimeData()
                clipboard = QApplication.clipboard()
                A = AnkiLinksCopy2
                B = AnkiLinksCopy2.Open
                C = AnkiLinksCopy2.Open.Gview
                header = f"{A.protocol}://{B.command}?{C.key}="
                href = header + quote(data.uuid)

                func_dict = {
                        A.LinkType.htmllink  : lambda: f"""<a href="{href}">{Translate.Anki搜索}:{data.name}</a>""",
                        A.LinkType.orgmode   : lambda: f"[[{href}][{Translate.Anki搜索}:{data.name}]]",
                        A.LinkType.markdown  : lambda: f"[{Translate.Anki搜索}:{data.name}]({href})",
                        A.LinkType.htmlbutton: lambda: f"""<div >|<button class="hjp_bilink ankilink button" onclick="javascript:pycmd('{href}');">{Translate.Anki视图}:{data.name}</button>|</div>"""
                }
                if mode == A.LinkType.htmllink:
                    mmdata.setText(href)
                    mmdata.setHtml(func_dict[mode]())
                    clipboard.setMimeData(mmdata)
                else:
                    clipboard.setText(func_dict[mode]())
                tooltip(href)

    class LinkType:
        inAnki = 0
        htmlbutton = 1
        htmllink = 2
        markdown = 3
        orgmode = 4


class AnkiLinks:
    """这个版本已经废弃,仅用来兼容
    AnkiLinksCopy2存在无法运行的问题
    """

    class Type:
        html = 0
        markdown = 1
        orgmode = 2
        inAnki = 3

    @staticmethod
    def copy_card_as(linktype: int = None, pairs_li: 'list[G.objs.LinkDataPair]' = None, FROM=None):
        tooltip(pairs_li.__str__())
        clipboard = QApplication.clipboard()
        header = f"{G.src.ankilink.protocol}://opencard_id="
        if FROM == DataFROM.shortCut:
            pairs_li = BrowserOperation.get_selected_card()
            linktype = Config.get().default_copylink_mode.value

        def as_html(pairs_li: 'list[G.objs.LinkDataPair]'):
            total = ""
            puretext = ""
            for pair in pairs_li:
                total += f"""<a href="{header}{pair.card_id}">{pair.desc}<a><br>""" + "\n"
                puretext += f"""{header}{pair.card_id}\n"""
            mmdata = QMimeData()
            mmdata.setHtml(total)
            mmdata.setText(puretext)
            clipboard.setMimeData(mmdata)
            # clipboard.setText(total)
            pass

        def as_inAnki(pairs_li: 'list[G.objs.LinkDataPair]'):
            total = ""

            def buttonmaker(p: LinkDataPair):
                return f"""<div >|<button class="hjp_bilink ankilink button" onclick="javascript:pycmd('{header}{p.card_id}');">{p.desc}</button>|</div>"""

            for pair in pairs_li:
                total += buttonmaker(pair)
            clipboard.setText(total)

        def as_markdown(pairs_li: 'list[G.objs.LinkDataPair]'):
            total = ""
            for pair in pairs_li:
                total += f"""[{pair.desc}]({header}{pair.card_id})\n"""
            clipboard.setText(total)
            pass

        def as_orgmode(pairs_li: 'list[G.objs.LinkDataPair]'):
            total = ""
            for pair in pairs_li:
                total += f"""[[{header}{pair.card_id}][{pair.desc}]]\n"""
            clipboard.setText(total)
            pass

        typ = AnkiLinks.Type
        func_dict = {typ.html    : as_html,
                     typ.orgmode : as_orgmode,
                     typ.markdown: as_markdown,
                     typ.inAnki  : as_inAnki}
        func_dict[linktype](pairs_li)
        if len(pairs_li) > 0:
            tooltip(clipboard.text())
        else:
            tooltip(Translate.请选择卡片)

    @staticmethod
    def copy_search_as(linktype: int, browser: "Browser"):
        searchstring = browser.form.searchEdit.currentText()
        tooltip(searchstring)
        clipboard = QApplication.clipboard()
        header = f"{G.src.ankilink.protocol}://openbrowser_search="
        href = header + quote(searchstring)

        def as_html():
            total = f"""<a href="{href}">{Translate.Anki搜索}:{searchstring}</a>"""
            mmdata = QMimeData()
            mmdata.setHtml(total)
            mmdata.setText(href)
            clipboard.setMimeData(mmdata)
            pass

        def as_markdown():
            total = f"[{Translate.Anki搜索}:{searchstring}]({href})"
            clipboard.setText(total)
            pass

        def as_orgmode():
            total = f"[[{href}][{Translate.Anki搜索}:{searchstring}]]"
            clipboard.setText(total)
            pass

        typ = AnkiLinks.Type
        func_dict = {typ.html    : as_html,
                     typ.orgmode : as_orgmode,
                     typ.markdown: as_markdown}
        func_dict[linktype]()
        pass

    @staticmethod
    def copy_gview_as(linktype: int, data: "GViewData"):
        tooltip(data.__str__())
        clipboard = QApplication.clipboard()
        header = f"{G.src.ankilink.protocol}://opengview_id="
        href = header + quote(data.uuid)

        def as_html():
            total = f"""<a href="{href}">{Translate.Anki视图}:{data.name}</a>"""
            mmdata = QMimeData()
            mmdata.setHtml(total)
            mmdata.setText(href)
            clipboard.setMimeData(mmdata)
            pass

        def as_inAnki():
            total = f"""<div >|<button class="hjp_bilink ankilink button" onclick="javascript:pycmd('{href}');">{Translate.Anki视图}:{data.name}</button>|</div>"""
            mmdata = QMimeData()
            mmdata.setHtml(total)
            mmdata.setText(href)
            # clipboard.setMimeData(mmdata)
            clipboard.setText(total)

        def as_markdown():
            total = f"[{Translate.Anki视图}:{data.name}]({href})"
            clipboard.setText(total)
            pass

        def as_orgmode():
            total = f"[[{href}][{Translate.Anki视图}:{data.name}]]"
            clipboard.setText(total)
            pass

        typ = AnkiLinks.Type
        func_dict = {typ.html    : as_html,
                     typ.orgmode : as_orgmode,
                     typ.markdown: as_markdown,
                     typ.inAnki  : as_inAnki, }
        func_dict[linktype]()

    @staticmethod
    def get_card_from_clipboard():
        from ..bilink.linkdata_admin import read_card_link_info
        clipboard = QApplication.clipboard()
        cliptext = clipboard.text()
        reg_str = fr"(?:{G.src.ankilink.protocol}://opencard_id=|\[\[link:)(\d+)"
        pair_li = [read_card_link_info(card_id).self_data for card_id in re.findall(reg_str, cliptext)]
        return pair_li


class PDFLink:
    @staticmethod
    def FindIndexOfPathInPreset(url: "str"):
        booklist = Config.get().PDFLink_presets.value  # [["PDFpath", "name", "style", "showPage"]...]
        a = [url == bookunit[0] for bookunit in booklist]
        if True in a:
            return a.index(True)
        else:
            return -1

    @staticmethod
    def GetPathInfoFromPreset(url):
        booklist = Config.get().PDFLink_presets.value  # [["PDFpath", "name", "style", "showPage"]...]
        index: "int" = PDFLink.FindIndexOfPathInPreset(url)
        if index != -1:
            return booklist[index]
        else:
            return None


def copy_intext_links(pairs_li: 'list[G.objs.LinkDataPair]'):
    def linkformat(card_id, desc):
        return f"""[[link:{card_id}_{desc}_]]"""

    copylinkLi = [linkformat(pair.card_id, pair.desc) for pair in pairs_li]
    clipstring = "\n".join(copylinkLi)
    if clipstring == "":
        tooltip(f"""{Translate.未选择卡片}""")
    else:
        clipboard = QApplication.clipboard()
        clipboard.setText(clipstring)
        tooltip(f"""{Translate.已复制到剪贴板}：{clipstring}""")
    pass


def on_clipper_closed_handle():
    from . import G
    G.mw_win_clipper = None


def event_handle_connect(event_dict):
    for event, handle in event_dict:
        event.connect(handle)
    return event_dict


def event_handle_disconnect(event_dict: "list[list[pyqtSignal,callable]]"):
    for event, handle in event_dict:
        try:
            # print(event.signal)
            event.disconnect(handle)
            # print(f"""{event.__str__()} still has {}  connects""")
        except Exception:
            # print(f"{event.__str__()} do not connect to {handle.__str__()}")
            pass


def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def version_cmpkey(path):
    from . import objs
    filename = os.path.basename(path)
    v_tuple = re.search(r"(\d+)\.(\d+)\.(\d+)", filename).groups()
    return objs.AddonVersion(v_tuple)



def data_crashed_report(data):
    from . import G
    path = G.src.path.data_crash_log
    showInfo(f"你的卡片链接信息读取失败,相关的失败数据已经保存到{path},请联系作者\n"
             f"Your card link information failed to read, the related failure data has been saved to{path}, please contact the author")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caller = sys._getframe(1).f_code.co_name
    filename = sys._getframe(1).f_code.co_filename
    line_number = sys._getframe(1).f_lineno
    data_string = data.__str__()
    info = f"""\n{filename}\n{timestamp} {caller} {line_number}\n{data_string}"""
    if not os.path.exists(path):
        f = open(path, "w", encoding="utf-8")
    else:
        f = open(path, "a", encoding="utf-8")
    f.write(info)


class Geometry:
    @staticmethod
    def MakeArrowForLine(line: "QLineF"):
        v = line.unitVector()
        v.setLength(30)
        v.translate(QPointF(line.dx() * 2 / 5, line.dy() * 2 / 5))

        n = v.normalVector()
        n.setLength(n.length() * 0.3)
        n2 = n.normalVector().normalVector()

        p1 = v.p2()
        p2 = n.p2()
        p3 = n2.p2()
        return QPolygonF([p1, p2, p3])

    @staticmethod
    def IntersectPointByLineAndRect(line: "QLineF", polygon: "QRectF"):
        intersectPoint = QPointF()
        edges = [
                QLineF(polygon.topLeft(), polygon.topRight()),
                QLineF(polygon.topLeft(), polygon.bottomLeft()),
                QLineF(polygon.bottomRight(), polygon.bottomLeft()),
                QLineF(polygon.bottomRight(), polygon.topRight()),
        ]
        # edges = Map.do(range(4),lambda i:QLineF(polygon.at(i),polygon.at((i+1)%4)))
        # print(f"edges={edges},\nLine={line}")
        for edge in edges:
            intersectsType, pointAt = line.intersects(edge)

            if intersectsType == QLineF.IntersectionType.BoundedIntersection:
                return intersectPoint
        return None


CardId = Compatible.CardId()
log = logger(__name__)
