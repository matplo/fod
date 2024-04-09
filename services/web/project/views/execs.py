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
import time
import subprocess
import shlex
import os
from project import app
from project.scripts.exec_result import exec_result

bp = Blueprint('execs', __name__)


@bp.route('/formexec/<path:path>/', methods=['GET', 'POST'])
@login_required
def formexec(path):
    page = flatpages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    execute = page.meta.get('execute', None)
    form_module_name = page.meta.get('formexec', None)
    form_module = __import__(f'project.scripts.external.{form_module_name}', fromlist=['Form'])
    form = getattr(form_module, 'Form')
    if form.validate_on_submit():
        if execute is not None:
            return render_template(template, page=page, form=form, result=exec_result(execute, form.data))
    return render_template(template, page=page, form=form, result=None)


@bp.route('/form/<path:path>/', methods=['GET', 'POST'])
@login_required
def form(path):
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
    page = flatpages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    variable = request.args.get('q', None)
    if variable is None or len(variable) == 0:
        return redirect(url_for('execs.batch', q='No command provided'))
    else:
        cmnd_output_file, _ = process_input(variable)
        time.sleep(0.1)  # sleep briefly before trying to stream
        stream_source = f'/stream_file?q={cmnd_output_file}'
    return render_template(template, page=page, stream_source=stream_source)


@bp.route('/stream_file')
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


@bp.route('/execute_script')
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


@bp.route("/upload", methods=["GET", "POST"])
@login_required
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
