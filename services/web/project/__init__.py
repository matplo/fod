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
from werkzeug.security import generate_password_hash, check_password_hash

from flask_bootstrap import Bootstrap
from flask_flatpages import FlatPages
from flask_login import (
    LoginManager,
    UserMixin,
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
)

from .forms import MyForm, LoginForm
from .process_input import process_input

import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.debug = False
login_manager = LoginManager()
login_manager.init_app(app)
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


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)  # new line
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(1024))
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, username, email, password_hash, active):  # updated line
        self.username = username  # new line
        self.email = email
        # self.password_hash = generate_password_hash(password)
        # we assume password is stored as hashed password
        self.password_hash = password_hash
        self.active = active

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    page = flatpages.get_or_404('login')
    template = page.meta.get('template', 'page.html')
    # replace with actual form
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('result', q='login successful'))
        else:
            return redirect(url_for('result', q='login failed'))
    return render_template(template, page=page, pages=flatpages, form=form, _external=False)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('result', q='logout successful'))


@app.route('/<path:path>/')
def page(path):
    page = flatpages.get_or_404(path)
    if page.meta.get('form', None) == 'True':
        return redirect(url_for('form', path=path))
    template = page.meta.get('template', 'page.html')
    return render_template(template, page=page, pages=flatpages, _external=False)


@app.route('/form/<path:path>/', methods=['GET', 'POST'])
@login_required
def form(path):
    page = flatpages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    form = MyForm()
    if form.validate_on_submit():
        text = form.text.data
        flash('Form submitted successfully.')
        return redirect(url_for('result', q=text))
    return render_template(template, page=page, pages=flatpages, form=form, _external=False)


@app.route('/result', methods=['GET', 'POST'])
def result(path='result'):
    page = flatpages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    variable = request.args.get('q', None)
    result = process_input(variable)
    return render_template(template, page=page, pages=flatpages, result=result, _external=False)


@app.route("/")
def default_page():
    return page('home')


@app.errorhandler(Exception)
def handle_exception(e):
    # get the error number
    error_number = getattr(e, 'code', 500)  # default to 500 if no 'code' attribute
    # pass the error to the template
    return render_template('error.html', error=e, error_number=error_number, pages=flatpages, _external=False), error_number


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
