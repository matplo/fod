import os
from flask_bootstrap import Bootstrap4
from flask import (
    Flask,
    render_template,
    render_template_string,
    g,
)
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_flatpages import FlatPages
from flask_login import (
    LoginManager,
    current_user,
)
# sys.path.append(os.path.dirname(__file__))
from project.scripts.redis_store import RedisStoreApp
from project.scripts.page_data import PageDataExtension
from .config import update_dict_from_yaml

import markdown
import project.scripts.utils as putils

from jinja2 import Environment, select_autoescape

# Create the Flask app
app = Flask(__name__)

@app.template_filter('JTEST_FILTERED_is_string')
def JTEST_FILTERED_is_string(value):
    return isinstance(value, str)

app.jinja_env.tests['JTEST_FILTERED_is_string'] = JTEST_FILTERED_is_string


# Set up the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
# Set up the bootstrap
bs = Bootstrap4(app)
# Set up the flatpages
flatpages = FlatPages(app)
app.config.from_object("project.config.Config")
# note you can leave config.py alone and use config.yaml to override settings
update_dict_from_yaml(app.config)
app.debug = app.config['DEBUG']

from project.scripts.custom_render import custom_render
# Define the markdown renderer
def custom_render_template(text):
    prerendered_body = render_template_string(text)
    md_body = markdown.markdown(prerendered_body, extensions=app.config['FLATPAGES_MARKDOWN_EXTENSIONS'])
    return custom_render(md_body)


# Set up the custom renderer
app.config['FLATPAGES_HTML_RENDERER'] = custom_render_template
# this is important for docker/nginx setup
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
# Set up logging
logger = putils.setup_logger(__name__)
# Set up the database
db = SQLAlchemy(app)
# Set up the redis store custom class
redis_store = RedisStoreApp()
redis_store.init_app(app)
# Set up the pdata extension
pdata_ext = PageDataExtension(app)


# import models here
from project.models.user import User
# Register blueprints here
# import project.scripts.utils as putils
putils.register_blueprints_from_dir(os.path.join(os.path.dirname(__file__), 'views'), app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def before_request():
    g.page = None
    g.pages = flatpages
    g.pdata = pdata_ext.data
    g.user = current_user
    g.redis = redis_store
    g.pdata.meta = None
    g.pdata.form = None
    g.pdata.qs_list = None
    g.pdata.last_qs = None
    g.config = app.config


@app.errorhandler(Exception)
def handle_exception(e):
    # get the error number
    error_number = getattr(e, 'code', 500)  # default to 500 if no 'code' attribute
    # pass the error to the template
    return render_template('error.html', error=e, error_number=error_number), error_number


# setup debug toolbar
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['DEBUG_TB_PANELS'] = [
    'flask_debugtoolbar.panels.versions.VersionDebugPanel',
    'flask_debugtoolbar.panels.timer.TimerDebugPanel',
    'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
    'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
    'flask_debugtoolbar.panels.template.TemplateDebugPanel',
    'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
    'flask_debugtoolbar.panels.logger.LoggingPanel',
    'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
    # Comment out the next line to disable the "g" panel
    'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
]
toolbar = DebugToolbarExtension(app)
