import sys
import types
from pathlib import Path


SYSTEM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SYSTEM_ROOT.parents[1]

for path in (str(SYSTEM_ROOT), str(REPO_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)


# создаём фейковый модуль flask
fake_flask = types.ModuleType("flask")


# минимальный Flask класс (SDK его импортирует)
class Flask:
    def __init__(self, *args, **kwargs):
        pass

    def route(self, *args, **kwargs):
        def wrapper(f):
            return f
        return wrapper


# jsonify тоже часто используется
def jsonify(*args, **kwargs):
    return {}


fake_flask.Flask = Flask
fake_flask.jsonify = jsonify


sys.modules["flask"] = fake_flask
