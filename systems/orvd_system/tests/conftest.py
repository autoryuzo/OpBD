import sys
import types


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