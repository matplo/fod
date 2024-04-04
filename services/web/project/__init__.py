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
    Response,
    stream_with_context,
)

import subprocess
import shlex
import time

from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash

from flask_bootstrap import Bootstrap
from flask_flatpages import FlatPages
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_user,
    logout_user,
    login_required,
)

from .forms import MyForm, LoginForm
from .process_input import process_input
from .redis_store import RedisStoreApp, RedisStoreExecFiles
from .page_data import PageData

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
redis_store = RedisStoreApp()
redis_store.init_app(app)


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
    # return redirect(url_for('result', q='logout successful'))
    return redirect(url_for('page', path='home'))


@app.route('/<path:path>/')
def page(path):
    page = flatpages.get_or_404(path)
    if page.meta.get('form', None) == 'True':
        return redirect(url_for('form', path=path))
    template = page.meta.get('template', 'page.html')
    pdata = PageData()
    pdata.meta = page.meta
    pdata.redis = redis_store
    pdata.init_name = __name__
    if path == 'list_qs':
        if redis_store.files:
            pdata.qs = redis_store.files.get_files_dict()
        else:
            pdata.qs = []
    return render_template(template, page=page, pages=flatpages, pdata=pdata, _external=False)


@app.route('/form/<path:path>/', methods=['GET', 'POST'])
@login_required
def form(path):
    page = flatpages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    form = MyForm()
    if form.validate_on_submit():
        text = form.text.data
        flash('Form submitted successfully.')
        if '.x' == text[:2]:
            return redirect(url_for('stream', q=text[3:]))
        return redirect(url_for("result", q=text))
    return render_template(template, page=page, pages=flatpages, form=form, _external=False)


@app.route('/result', methods=['GET', 'POST'])
@login_required
def result(path='result'):
    page = flatpages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    variable = request.args.get('q', None)
    result_fout, pid = process_input(variable, link=True)
    redis_store.files.add_file(result_fout, pid)
    with open(result_fout, 'r') as f:
        lines = f.readlines()
    return render_template(template, page=page, pages=flatpages, result='\n'.join(lines), _external=False)


@app.route('/stream', methods=['GET', 'POST'])
@login_required
def stream(path='stream'):
    page = flatpages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    variable = request.args.get('q', None)
    if variable is None or len(variable) == 0:
        return redirect(url_for('result', q='No command provided'))
    else:
        cmnd_output_file, _ = process_input(variable)
        time.sleep(0.1)  # sleep briefly before trying to stream
        stream_source = f'/stream_file?q={cmnd_output_file}'
    return render_template(template, page=page, pages=flatpages, stream_source=stream_source, _external=False)


@app.route('/stream_file')
@login_required
def stream_file():
    def generate():
        filename = request.args.get('q', None)
        with open(filename, 'r') as f:
            lines = f.readlines()
        for line in lines:
            yield f"{line}"
    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.implicit_sequence_conversion = True
    return response


@app.route('/execute_script')
@login_required
def execute_script():
    def generate():
        # Command to execute the Python script
        command = request.args.get('q', None)
        if command is None:
            yield 'No command provided'
            return
        # Setup the process to capture stdout and stderr
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Stream both stdout and stderr
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                yield f"data: {output.decode()}\n\n"
        # After the process ends, check and stream stderr if there was any error
        error = process.stderr.read().decode()
        if error:
            yield f"data: ERROR: {error}\n\n"
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


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
@login_required
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
