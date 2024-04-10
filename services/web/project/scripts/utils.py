# utils.py
import logging.handlers
import os
import importlib.util
import fnmatch
import logging

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # handler = logging.FileHandler('app.log')
    handler = logging.handlers.RotatingFileHandler('/home/app/web/app.log', maxBytes=10000, backupCount=0)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def find_files(rootdir='.', pattern='*'):
    return [os.path.join(rootdir, filename)
            for rootdir, dirnames, filenames in os.walk(rootdir)
            for filename in filenames
            if fnmatch.fnmatch(filename, pattern)]

# instead of
# from project.views.home import bp as home_bp
# app.register_blueprint(home_bp)
# ...
# the below we use importlib
def register_blueprints_from_dir(view_dir, app):
    for filename in find_files(view_dir, '*.py'):
        module_name = os.path.basename(filename)[:-3]  # remove the .py extension
        if module_name == '__init__':
            continue
        module_path = filename
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        app.register_blueprint(module.bp)
