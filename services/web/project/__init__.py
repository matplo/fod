import os

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    render_template,
    flash,
    redirect,
    url_for,
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix

from flask_bootstrap import Bootstrap
from flask_flatpages import FlatPages

from .forms import MyForm

import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.debug = True
bs = Bootstrap(app)
flatpages = FlatPages(app)
app.config.from_object("project.config.Config")
print(app.config)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Set up logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=0)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email


@app.route('/<path:path>/')
def page(path):
    page = flatpages.get_or_404(path)
    if page.meta.get('form', None) == 'True':
        return redirect(url_for('form', path=path))
    template = page.meta.get('template', 'page.html')
    return render_template(template, page=page, pages=flatpages, _external=False)


@app.route('/form/<path:path>/', methods=['GET', 'POST'])
def form(path):
    page = flatpages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    form = MyForm()
    if form.validate_on_submit():
        text = form.text.data
        flash('Form submitted successfully.')
        return redirect(url_for('page', path=text))
    return render_template(template, page=page, pages=flatpages, form=form, _external=False)


@app.route("/")
def default_page():
    return page('home')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', error=e, pages=flatpages, _external=False), 404


@app.errorhandler(500)
def error_500(e):
    # note that we set the 500 status explicitly
    return render_template('500.html', error=e, pages=flatpages, _external=False), 500


@app.errorhandler(502)
def error_502(e):
    # note that we set the 502 status explicitly
    return render_template('502.html', error=e, pages=flatpages, _external=False), 502


@app.errorhandler(Exception)
def handle_exception(e):
    # pass the error to the template
    return render_template('error.html', error=e, pages=flatpages, _external=False), 500


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """
