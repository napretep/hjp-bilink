class AllEvent:
    def __init__(self, eventType=None, sender=None):
        self.Type = eventType
        self.sender = sender


class PDFPrevSaveClipboxEvent(AllEvent):
    beginType = 0
    endType = 1

    def __init__(self, eventType=None, sender=None, data=None, callback=None, progress_signal=None,
                 worker_quit_signal=None):
        super().__init__(eventType, sender)
        self.data = data  # 数据
        self.worker_quit_signal = worker_quit_signal
        self.callback = callback  # 结束时调用,
        self.progress_signal = progress_signal  # 进度条
