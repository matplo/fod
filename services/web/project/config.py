import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/project/media"
    FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', 'fenced_code']
    TEMPLATE_FOLDER = f"{os.getenv('APP_FOLDER')}/project/templates"
    FLATPAGES_ROOT = f"{os.getenv('APP_FOLDER')}/project/pages"
    FLATPAGES_EXTENSION = ".md"
    FLATPAGES_AUTO_RELOAD = True
    FLATPAGES_EXTENSION_CONFIGS = {
        'codehilite': {
            'linenums': True
        }
    }
    SECRET_KEY = 'TEST_APP_SECRET_KEY'
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    # SERVER_NAME = 'localhost:1337' - not needed with ProxyFix
    WEB_TITLE = 'Test App'