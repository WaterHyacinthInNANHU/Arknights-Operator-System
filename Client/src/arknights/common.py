from time import sleep


class ClickNoEffect(Exception):
    pass


class NothingMatched(Exception):
    pass


class UnknownInterface(Exception):
    pass


class InvalidInitialInterface(Exception):
    pass


class NoSufficientSanity(Exception):
    pass


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


class MaxRetried(Exception):
    pass


def retry_on_exception(exception, max_times: int, retry_interval_sec: float, raise_error: bool = True):
    def decorator(function):
        def wrapper(*args, **kwargs):
            assert max_times >= 0
            assert retry_interval_sec >= 0
            for _ in range(max_times):
                try:
                    result = function(*args, **kwargs)
                except exception:
                    sleep(retry_interval_sec)
                else:
                    break
            else:
                raise MaxRetried
            return result
        return wrapper
    return decorator
