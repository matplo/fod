# utils.py
import os
import importlib.util
from project import app


# instead of
# from project.views.home import bp as home_bp
# app.register_blueprint(home_bp)
# ...
# the below we use importlib
def register_blueprints_from_dir(view_dir):
    for filename in os.listdir(view_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # remove the .py extension
            module_path = os.path.join(view_dir, filename)
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            app.register_blueprint(module.bp)
