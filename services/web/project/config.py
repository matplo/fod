import os
import yaml


basedir = os.path.abspath(os.path.dirname(__file__))
if os.getenv('APP_FOLDER') is None:
    os.environ['APP_FOLDER'] = os.path.dirname(basedir)


def _normalize_db_url(url):
    if not url:
        return "sqlite://"
    # SQLAlchemy 2.1+ defaults postgresql:// to psycopg (v3). Map to psycopg2 if no driver explicitly specified.
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


class Config(object):
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.getenv("DATABASE_URL", "sqlite://"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/project/media"
    FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', 'fenced_code', 'tables', 'smarty', 'toc']
    TEMPLATE_FOLDER = f"{os.getenv('APP_FOLDER')}/project/templates"
    FLATPAGES_ROOT = f"{os.getenv('APP_FOLDER')}/project/pages"
    FLATPAGES_EXTENSION = ".md"
    FLATPAGES_AUTO_RELOAD = True
    FLATPAGES_EXTENSION_CONFIGS = {
        'codehilite': {
            'linenums': True
        }
    }
    SECRET_KEY = os.getenv('SECRET_KEY', 'TEST_APP_SECRET_KEY')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    # SERVER_NAME = 'localhost:1337' - not needed with ProxyFix
    WEB_TITLE = os.getenv('WEB_TITLE', 'FOD Web')
    WEB_DESCRIPTION = os.getenv('WEB_DESCRIPTION', 'Flask on Docker App')
    APP_YAML_CONFIG = f"{os.getenv('APP_FOLDER')}/project/config.yaml"
    BOOTSTRAP_SERVE_LOCAL = False


def update_dict_from_yaml(d, yml=Config.APP_YAML_CONFIG):
    """Load base YAML config and any override YAMLs from the config.d drop-in directory."""
    if os.path.isfile(yml):
        with open(yml, 'r') as f:
            base_conf = yaml.safe_load(f)
            if base_conf:
                d.update(base_conf)

    # Check for drop-in modular configs in project/config.d/*.yaml
    config_d = os.path.join(os.path.dirname(yml), 'config.d')
    if os.path.isdir(config_d):
        for fname in sorted(os.listdir(config_d)):
            if fname.endswith(('.yaml', '.yml')):
                extra_path = os.path.join(config_d, fname)
                try:
                    with open(extra_path, 'r') as f:
                        mod_conf = yaml.safe_load(f)
                        if mod_conf:
                            d.update(mod_conf)
                except Exception as e:
                    print(f"Warning: Failed to load modular config {extra_path}: {e}")
