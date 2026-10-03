# utils.py
import logging.handlers
import os
import importlib.util
import fnmatch
import logging

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    log_dir = os.getenv('APP_FOLDER', '.')
    log_file = os.path.join(log_dir, 'app.log')
    try:
        handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=100000, backupCount=2)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except Exception:
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(console)
    return logger


def find_files(rootdir='.', pattern='*'):
    return [os.path.join(rootdir, filename)
            for rootdir, dirnames, filenames in os.walk(rootdir)
            for filename in filenames
            if fnmatch.fnmatch(filename, pattern)]


def register_blueprints_from_dir(view_dir, app):
    """Dynamically register any Flask blueprints found in Python files under view_dir."""
    if not os.path.isdir(view_dir):
        return
    for filename in sorted(find_files(view_dir, '*.py')):
        base = os.path.basename(filename)[:-3]
        if base == '__init__':
            continue
        rel_path = os.path.relpath(filename, view_dir)
        module_name = "bp_" + rel_path.replace(os.path.sep, "_")[:-3]
        try:
            spec = importlib.util.spec_from_file_location(module_name, filename)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                bp = getattr(module, 'bp', None)
                if bp is not None and bp.name not in app.blueprints:
                    app.register_blueprint(bp)
        except Exception as e:
            logging.getLogger('project').error(f"Failed to load blueprint from {filename}: {e}")
