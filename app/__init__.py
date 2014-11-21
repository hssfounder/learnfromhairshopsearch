from .factory import _create_app

def create_app(instance_path=None, config=None):
    return _create_app(__name__, __path__, instance_path, config)
