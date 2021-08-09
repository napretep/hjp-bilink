from . import funcs


def signal_wrapper(signal=None, **signal_kwargs):
    def wrapper(func):
        def do(*args, **kwargs):
            result = func(*args, **kwargs)
            if signal is not None:
                signal.emit(signal_kwargs)
            return result

        return do

    return wrapper


def func_wrapper(before=None, after=None):
    """
    Args:
        before: list[callable]
        funcli: list[callable]
        **signal_kwargs:

    Returns:

    """

    def wrapper(func):
        def do(*args, **kwargs):
            if before is not None:
                for f in before:
                    f(*args, **kwargs)
            result = func(*args, **kwargs)
            if after is not None:
                for f in after:
                    f(*args, **kwargs)
            return result

        return do

    return wrapper


def Previewer_close_wrapper(func):
    def do(self, QCloseEvent):
        result = func(self, QCloseEvent)
        if self.card() is not None:
            funcs.PDFprev_close(self.card().id, all=True)
        return result

    return do


def BrowserPreviewer_card_change_wrapper(func):
    def do(self):
        funcs.PDFprev_close(self.card().id, all=True)
        result = func(self)
        return result

    return do
