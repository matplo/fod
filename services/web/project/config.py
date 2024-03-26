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
    # SERVER_NAME = 'localhost:1337'
