import os
import sys
from typing import Union

from ..fitz import fitz
from PyQt5.QtCore import QItemSelection, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QStandardItemModel, QImage, QPixmap
import uuid
import logging
import tempfile


def pdf_page_unique(results):
    d = {}
    for record in results:
        if record["pdfuuid"] not in d:
            d[record["pdfuuid"]] = {"pagenum": set(), "pdfname": record["pdfname"]}
        d[record["pdfuuid"]]["pagenum"].add(record["pagenum"])
    return d


def pdf_uuid_read(uuid):
    pass


def show_clipbox_state():
    from . import ALL, events
    e = events.ClipboxStateSwitchEvent
    ALL.signals.on_clipboxstate_switch.emit(e(eventType=e.showType))


def clipboxstate_switch_done(show=True):
    from . import ALL, events
    e = events.ClipboxStateSwitchEvent
    ALL.signals.on_clipboxstate_switch.emit(
        e(eventType=e.showedType if show else e.hiddenType)
    )


def event_handle_connect(event_dict):
    for event, handle in event_dict.items():
        event.connect(handle)
    return event_dict


def event_handle_disconnect(event_dict: "dict[pyqtSignal,callable]"):
    for event, handle in event_dict.items():
        try:
            # print(event.signal)
            event.disconnect(handle)
            # print(f"""{event.__str__()} still has {}  connects""")
        except Exception:
            # print(f"{event.__str__()} do not connect to {handle.__str__()}")
            pass


def logger(logname=None, level=None, allhandler=None):
    from . import ALL
    if ALL.ISDEBUG:
        if logname is None:
            logname = "hjp_clipper"
        if level is None:
            level = ALL.DEBUG_LEVEL
        printer = logging.getLogger(logname)
        printer.setLevel(level)
        from .SrcAdmin_ import Get
        log_dir = os.path.join(Get.dir_root, "log.txt")

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
        return printer.debug, printer
    else:
        return do_nothing, do_nothing


qianziwen = "天地玄黄宇宙洪荒日月盈昃辰宿列张" \
            "寒来暑往秋收冬藏闰余成岁律吕调阳" \
            "云腾致雨露结为霜金生丽水玉出昆冈" \
            "剑号巨阙珠称夜光果珍李柰菜重芥姜" \
            "海咸河淡鳞潜羽翔龙师火帝鸟官人皇" \
            "始制文字乃服衣裳推位让国有虞陶唐" \
            "吊民伐罪周发殷汤坐朝问道垂拱平章" \
            "爱育黎首臣伏戎羌遐迩一体率宾归王" \
            "鸣凤在竹白驹食场化被草木赖及万方" \
            "盖此身发四大五常恭惟鞠养岂敢毁伤" \
            "女慕贞洁男效才良知过必改得能莫忘" \
            "罔谈彼短靡恃己长信使可覆器欲难量" \
            "墨悲丝染诗赞羔羊景行维贤克念作圣" \
            "德建名立形端表正空谷传声虚堂习听" \
            "祸因恶积福缘善庆尺璧非宝寸阴是竞" \
            "资父事君曰严与敬孝当竭力忠则尽命" \
            "临深履薄夙兴温凊似兰斯馨如松之盛" \
            "川流不息渊澄取映容止若思言辞安定" \
            "笃初诚美慎终宜令荣业所基籍甚无竟" \
            "学优登仕摄职从政存以甘棠去而益咏" \
            "乐殊贵贱礼别尊卑上和下睦夫唱妇随" \
            "外受傅训入奉母仪诸姑伯叔犹子比儿" \
            "孔怀兄弟同气连枝交友投分切磨箴规" \
            "仁慈隐恻造次弗离节义廉退颠沛匪亏" \
            "性静情逸心动神疲守真志满逐物意移" \
            "坚持雅操好爵自縻都邑华夏东西二京" \
            "背邙面洛浮渭据泾宫殿盘郁楼观飞惊" \
            "图写禽兽画彩仙灵丙舍旁启甲帐对楹" \
            "肆筵设席鼓瑟吹笙升阶纳陛弁转疑星" \
            "右通广内左达承明既集坟典亦聚群英" \
            "杜稿钟隶漆书壁经府罗将相路侠槐卿" \
            "户封八县家给千兵高冠陪辇驱毂振缨" \
            "世禄侈富车驾肥轻策功茂实勒碑刻铭" \
            "盘溪伊尹佐时阿衡奄宅曲阜微旦孰营" \
            "桓公匡合济弱扶倾绮回汉惠说感武丁" \
            "俊义密勿多士实宁晋楚更霸赵魏困横" \
            "假途灭虢践土会盟何遵约法韩弊烦刑" \
            "起翦颇牧用军最精宣威沙漠驰誉丹青" \
            "九州禹迹百郡秦并岳宗泰岱禅主云亭" \
            "雁门紫塞鸡田赤诚昆池碣石钜野洞庭" \
            "旷远绵邈岩岫杳冥治本于农务兹稼穑" \
            "俶载南亩我艺黍稷税熟贡新劝赏黜陟" \
            "孟轲敦素史鱼秉直庶几中庸劳谦谨敕" \
            "聆音察理鉴貌辨色贻厥嘉猷勉其祗植" \
            "省躬讥诫宠增抗极殆辱近耻林皋幸即" \
            "两疏见机解组谁逼索居闲处沉默寂寥" \
            "求古寻论散虑逍遥欣奏累遣戚谢欢招" \
            "渠荷的历园莽抽条枇杷晚翠梧桐蚤凋" \
            "陈根委翳落叶飘摇游鹍独运凌摩绛霄" \
            "耽读玩市寓目囊箱易輶攸畏属耳垣墙" \
            "具膳餐饭适口充肠饱饫烹宰饥厌糟糠" \
            "亲戚故旧老少异粮妾御绩纺侍巾帷房" \
            "纨扇圆洁银烛炜煌昼眠夕寐蓝笋象床" \
            "弦歌酒宴接杯举殇矫手顿足悦豫且康" \
            "嫡后嗣续祭祀烝尝稽颡再拜悚惧恐惶" \
            "笺牒简要顾答审详骸垢想浴执热愿凉" \
            "驴骡犊特骇跃超骧诛斩贼盗捕获叛亡" \
            "布射僚丸嵇琴阮箫恬笔伦纸钧巧任钓" \
            "释纷利俗并皆佳妙毛施淑姿工颦妍笑" \
            "年矢每催曦晖朗曜璇玑悬斡晦魄环照" \
            "指薪修祜永绥吉劭矩步引领俯仰廊庙" \
            "束带矜庄徘徊瞻眺孤陋寡闻愚蒙等诮" \
            "谓语助者焉哉乎也" \
            "乾坤震巽坎艮兑戊庚辛壬癸巳午未申酉戌亥三六七十亿"

base_64_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789^*"


def baseN(num, b):
    return ((num == 0) and "0") or \
           (baseN(num // b, b).lstrip("0") + base_64_str[num % b])


def base32(num):
    return baseN(num, 32)


def base64(num):
    return baseN(num, 64)


def index_from_row(model: 'QStandardItemModel', row):
    """从模型给定的两个item划定一个index区域,用来模拟select"""
    idx1 = model.indexFromItem(row[0])
    idx2 = model.indexFromItem(row[1])
    return QItemSelection(idx1, idx2)


def str_shorten(string, length=30):
    if len(string) <= length:
        return string
    else:
        return string[0:int(length/2)-3]+"..."+string[-int(length/2):]


def pixmap_page_load(doc: "Union[fitz.Document,str]", pagenum, ratio=1, browser=False, browse_size: "QSize" = None,
                     callback=None):
    """从self.doc读取page,再转换为pixmap"""
    if type(doc) == str:
        doc = fitz.open(doc)
    pdfname = os.path.basename(doc.name)
    # print(f"pagenum={pagenum}")
    if callback:
        callback(f"pagenum={pagenum},")
    page: "fitz.Page" = doc.load_page(pagenum)  # 加载的是页面
    tempdir = tempfile.gettempdir()
    tempPNGname = os.path.join(tempdir, f"{pdfname[0:-4]}_{pagenum}_{ratio}.png")
    print, printer = logger(__name__)
    # print(tempPNGname)
    pix: "fitz.Pixmap" = page.getPixmap(matrix=fitz.Matrix(ratio, ratio))  # 将页面渲染为图片
    if not os.path.exists(tempPNGname):
        pix.save(tempPNGname)
    return tempPNGname
    # return QPixmap(tempPNGname)
    # print(f"page.mediabox_size{}")
    # if preview and len(pix.tobytes())>120000:
    #     pix.shrink(3)
    #     # print(f"after compress{len(pix.tobytes())}")
    # else:
    #     print(pix.size  )
    # print(ratio.__str__())

    # fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888  # 渲染的格式
    # pageImage = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
    #
    # pixmap = QPixmap()
    # pixmap.convertFromImage(pageImage)  # 转为pixmap
    # return QPixmap(pixmap)


def on_clipbox_addedToPageView(clipbox, cardlist, pageview):
    """涉及cardlist中的clipboxLi的添加"""

    pass


def clipbox_delete(clipbox, cardlist, pageview):
    pass


def uuidmake():
    return str(uuid.uuid4())


def wrapper_print_debug(func):
    """当程序在anki中运行的时候,无法看到打印的东西,必须输出到文件"""

    def wrapper(*args, **kwargs):
        from .ALL import ISDEBUG

        if ISDEBUG:
            log(args[0])
            return func(*args, **kwargs)
        else:
            return do_nothing(*args, **kwargs)


def log(text):
    from .SrcAdmin_ import Get

    logdir = os.path.join(Get.dir_root, "log.txt")
    f = open(logdir, "w+", encoding="utf-8")


def do_nothing(*args, **kwargs):
    pass


# print,_ = logger(__name__)

if __name__ == "__main__":
    pass
