from PyQt5.QtGui import QStandardItem


class SpecialTreeItem(QStandardItem):
    def __init__(self, itemname, character="card_id", level=0, primData=None):
        super().__init__(itemname)
        self.character = character
        self.level = level
        self.primData = primData

def item_insert_rows(parent,target,offset_posi:int,selected_rows:list):
    """
    Parameters
    ----------
    parent
    target
    offset_posi :偏移位置,比如插在target之前,+0,插在之后则+1
    selected_rows

    Returns
    -------

    """
    posi_row = target.row()
    temp_rows= []
    while parent.rowCount() > 0:
        temp_rows.append(parent.takeRow(0))
    final_rows = temp_rows[0:posi_row+offset_posi] + selected_rows + temp_rows[posi_row+offset_posi:]
    for row in final_rows:
        parent.appendRow(row)