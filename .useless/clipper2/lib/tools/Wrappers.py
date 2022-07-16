from . import funcs


def caller_restrict_wrapper(needCaller, needClass):
    def wrapper(func):
        def do(caller, *args, **kwargs):
            funcs.caller_check(needCaller, caller, needClass)
            result = func(*args, **kwargs)
            return result

        return do

    return wrapper


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
        before: list[list[callable,kwargs]]
        funcli: list[callable,kwargs]
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
                for f in before:
                    f(*args, **kwargs)
            return result

        return do

    return wrapper
