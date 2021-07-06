# url=https://github.com/dxstiny/py-flstudio-api/
# author=dxstiny

from enum import Enum

class Level(Enum):
    def __ge__(self, b):
        return self.value >= b.value

    trace = 0
    debug = 1
    info = 2
    warning = 3
    error = 4

_level = Level.warning

def SetLevel(level = Level.warning):
    global _level
    _level = level

class GetLogger():
    def __init__(self, name = "root"):
        self._name = name

    def trace(self, msg):
        self._log("TRACE", msg) if Level.trace >= _level else None

    def debug(self, msg):
        self._log("DEBUG", msg) if Level.debug >= _level else None

    def info(self, msg):
        self._log("INFO", msg) if Level.info >= _level else None

    def warning(self, msg):
        self._log("WARNING", msg) if Level.warning >= _level else None

    def error(self, msg):
        self._log("ERROR", msg) if Level.error >= _level else None

    def _log(self, type, msg):
        print(type + ":" + self._name + ":" + msg)
