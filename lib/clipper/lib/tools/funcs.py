from ..fitz import fitz
from PyQt5.QtCore import QItemSelection
from PyQt5.QtGui import QStandardItemModel, QImage, QPixmap


def index_from_row(model: 'QStandardItemModel', row):
    """从模型给定的两个item划定一个index区域,用来模拟select"""
    idx1 = model.indexFromItem(row[0])
    idx2 = model.indexFromItem(row[1])
    return QItemSelection(idx1, idx2)

def str_shorten(string,length=30):
    if len(string)<=length:
        return string
    else:
        return string[0:int(length/2)-3]+"..."+string[-int(length/2):]

def pixmap_page_load(doc, pagenum, ratio=1):
    """从self.doc读取page,再转换为pixmap"""
    page = doc.load_page(pagenum)  # 加载的是页面
    print(ratio.__str__())
    pix = page.getPixmap(matrix=fitz.Matrix(ratio, ratio))  # 将页面渲染为图片
    fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888  # 渲染的格式
    pageImage = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
    pixmap = QPixmap()
    pixmap.convertFromImage(pageImage)  # 转为pixmap
    return QPixmap(pixmap)


def on_clipbox_addedToPageView(clipbox, cardlist, pageview):
    """涉及cardlist中的clipboxLi的添加"""

    pass


def clipbox_delete(clipbox, cardlist, pageview):
    pass


if __name__ == "__main__":
    pass
