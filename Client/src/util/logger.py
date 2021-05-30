from colorama import Fore
from abc import ABC, abstractmethod
import os
from base64 import b64encode
from functools import lru_cache
from io import BytesIO


class Logger(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def info(self, s: str):
        pass

    @abstractmethod
    def debug(self, s: str):
        pass

    @abstractmethod
    def warning(self, s: str):
        pass

    @abstractmethod
    def error(self, s: str):
        pass


class CmdLogger(Logger):
    def info(self, s: str):
        print('({})'.format(self.name), end='')
        print('{}[INFO]{} '.format(Fore.GREEN, Fore.RESET), end='')
        print(s)

    def debug(self, s: str):
        print('({})'.format(self.name), end='')
        print('{}[DEBUG]{} '.format(Fore.MAGENTA, Fore.RESET), end='')
        print(s)

    def warning(self, s):
        print('({})'.format(self.name), end='')
        print('{}[WARNING]{} '.format(Fore.YELLOW, Fore.RESET), end='')
        print(s)

    def error(self, s: str):
        print('({})'.format(self.name), end='')
        print('{}[ERROR]{} '.format(Fore.RED, Fore.RESET), end='')
        print(s)


class RichLogger:
    def __init__(self, filename: str, overwrite=False):
        self.f = None
        self.filename = filename
        self.overwrite = overwrite

    def ensure_file(self):
        if self.f is not None:
            return
        self.f = open(self.filename, 'wb' if self.overwrite else 'ab')
        if self.f.tell() == 0:
            self.loghtml('<html><head><meta charset="utf-8"></head><body>')

    def logimage(self, image):
        self.ensure_file()
        bio = BytesIO()
        image.save(bio, format='PNG')
        imgb64 = b64encode(bio.getvalue())
        self.f.write(b'<p><img src="data:image/png;base64,%s" /></p>\n' % imgb64)
        self.f.flush()

    def logtext(self, text):
        self.ensure_file()
        self.loghtml('<pre>%s</pre>\n' % text)

    def loghtml(self, html):
        self.ensure_file()
        self.f.write(html.encode())
        self.f.flush()


@lru_cache(maxsize=None)
def get_logger(module):
    import config
    if config.get_instance_id() == 0:
        filename = '%s.html' % module
    else:
        filename = '%s.%d.html' % (module, config.get_instance_id())
    logger = RichLogger(os.path.join(config.logs, filename), True)
    return logger
