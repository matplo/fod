# execs.py

from flask_login import login_required
from flask import (
    Blueprint,
    flash,
    redirect,
    url_for,
    render_template,
    render_template_string,
    request,
    Response,
    stream_with_context,
)
from project.forms.base_forms import MyForm
from project.scripts.process_input import process_input
from project import flatpages, g
from werkzeug.utils import secure_filename
from project.forms.base_forms import UploadForm
import time
import subprocess
import shlex
import os
from project import app
from project.scripts.exec_result import exec_result
import project.scripts.utils as putils
logger = putils.setup_logger(__name__)


bp = Blueprint('execs', __name__)


@bp.route('/formexec/<path:path>/', methods=['GET', 'POST'])
@login_required
def formexec(path):
    page = flatpages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    execute = page.meta.get('execute', None)
    form_module_name = page.meta.get('formexec', None)
    form_module = __import__(f'project.forms.external.{form_module_name}', fromlist=['Form'])
    _form = getattr(form_module, 'Form')
    form = _form()
    if form.validate_on_submit():
        if execute is not None:
            return render_template(template, page=page, form=form, result=exec_result(execute, form.data))
    return render_template(template, page=page, form=form, result=None)


@bp.route('/form/<path:path>/', methods=['GET', 'POST'])
@login_required
def form(path):
    logger.info(f'/form path: {path}')
    page = flatpages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    form = MyForm()
    if form.validate_on_submit():
        text = form.text.data
        if '.x' == text[:2]:
            return redirect(url_for('execs.stream', q=text[3:]))
        return redirect(url_for("execs.batch", q=text))
    return render_template(template, page=page, form=form)


@bp.route('/batch', methods=['GET', 'POST'])
@login_required
def batch(path='batch'):
    logger.info(f'/batch path: {path}')
    # page = flatpages.get_or_404(path)
    # template = page.meta.get('template', 'page.html')
    variable = request.args.get('q', None)
    # the next line actually launches the command
    result_fout, pid = process_input(variable, link=True)
    g.pdata.last_qs = g.redis.files.add_file(result_fout, pid)
    return redirect(url_for('path.page', path='list_qs', q=result_fout))
    # with open(result_fout, 'r') as f:
    #    lines = f.readlines()
    # return render_template(template, page=page, result='<br>'.join(lines))


@bp.route('/stream', methods=['GET', 'POST'])
@login_required
def stream(path='stream'):
    logger.info(f'/stream path: {path}')
    page = flatpages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    variable = request.args.get('q', None)
    _ret_url = request.args.get('returl', None)
    _ret_path = request.args.get('retpath', None)
    if variable is None or len(variable) == 0:
        return redirect(url_for('execs.batch', q='No command provided'))
    else:
        cmnd_output_file, _ = process_input(variable)
        time.sleep(0.1)  # sleep briefly before trying to stream
        stream_source = f'/stream_file?q={cmnd_output_file}'
        return_url = {}
        if _ret_url is None or _ret_path is None:
            return_url['url'] = url_for('path.page', path='query')
            return_url['text'] = 'Return to Query Page'
        else:
            return_url['url'] = url_for(_ret_url, path=_ret_path, q=cmnd_output_file)
            # return_url['text'] = _ret_path
            return_url['text'] = f'Return to {return_url["url"]}'
    return render_template(template, page=page, stream_source=stream_source, return_url=return_url)


@bp.route('/stream_file')
@login_required
def stream_file():
    filename = request.args.get('q', None)
    if not filename:
        return "No file specified", 400

    # Ensure path stays strictly within allowed directories (proc_out or static)
    allowed_dirs = [
        os.path.abspath(os.path.join(app.config.get("STATIC_FOLDER", ""), "proc_out")),
        os.path.abspath(app.config.get("STATIC_FOLDER", "")),
    ]
    resolved = os.path.abspath(filename)
    if not any(
        resolved == adir or resolved.startswith(adir + os.sep)
        for adir in allowed_dirs
    ) or not os.path.isfile(resolved):
        logger.warning(f"Unauthorized or invalid stream_file request for path: {filename}")
        return "Access denied or file not found", 403

    try:
        with open(resolved, 'r', errors='replace') as f:
            content = f.read()
        return Response(content, mimetype='text/plain')
    except Exception as e:
        logger.error(f"Error reading stream file {resolved}: {e}")
        return f"Error reading file: {e}", 500


@bp.route('/execute_script')
@login_required
def execute_script():
    def generate():
        command = request.args.get('q', None)
        if command is None:
            yield "data: No command provided\n\n"
            return
        args = shlex.split(command)
        if not args:
            yield "data: Empty command\n\n"
            return

        # Security: confine execution to scripts inside project/scripts
        app_folder = os.getenv("APP_FOLDER", "/home/app/web")
        allowed_dirs = [
            os.path.abspath(os.path.join(app_folder, "project", "scripts")),
        ]
        cmd_path = os.path.abspath(args[0])
        if not any(cmd_path == d or cmd_path.startswith(d + os.sep) for d in allowed_dirs):
            yield f"data: Execution denied: command {args[0]} not in authorized directory\n\n"
            return

        try:
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                output = process.stdout.readline()
                if output == b'' and process.poll() is not None:
                    break
                if output:
                    yield f"data: {output.decode(errors='replace')}\n\n"
            error = process.stderr.read().decode(errors='replace')
            if error:
                yield f"data: ERROR: {error}\n\n"
        except Exception as ex:
            yield f"data: Process error: {str(ex)}\n\n"
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


# @bp.route("/upload", methods=["GET", "POST"])
# @login_required
# def upload_file():
#     if request.method == "POST":
#         file = request.files["file"]
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
#     return """
#     <!doctype html>
#     <title>upload new File</title>
#     <form action="" method=post enctype=multipart/form-data>
#       <p><input type=file name=file><input type=submit value=Upload>
#     </form>
#     """


@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    form = UploadForm()
    page = flatpages.get_or_404("upload")
    template = page.meta.get("template", "page.html")
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save(os.path.join(app.config["STATIC_FOLDER"], filename))
        flash(f"File {filename} uploaded successfully.", 'success')
        return redirect(url_for("execs.upload_file"))
    else:
        if len(form.errors):
            _serr = ' '.join([f"{k}: {v}" for k, v in form.errors.items()])
            flash(f"File upload failed. Errors: {_serr}", 'danger')
    return render_template(template, page=page, form=form)
