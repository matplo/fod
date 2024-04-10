# page.py
from flask import Blueprint, render_template, redirect, url_for, request
from project import flatpages, g
import project.scripts.utils as putils
logger = putils.setup_logger(__name__)


bp = Blueprint('path', __name__)


@bp.route('/<path:path>/')
def page(path):
    page = flatpages.get_or_404(path)
    logger.info(f'* path: {path}')
    logger.info(f'  ? routing: {page.meta.get("routing", None)}')
    if page.meta.get('routing', None) is not None:
        return redirect(url_for(page.meta.get('routing', None), path=path))
    logger.info(f'  ? form: {page.meta.get("form", None)}')
    if page.meta.get('form', None) is True:
        return redirect(url_for('execs.form', path=path))
    # if page.meta.get('formexec', None):
    #     return redirect(url_for('execs.formexec', path=path))
    template = page.meta.get('template', 'page.html')
    logger.info(f'template: {template}')
    g.pdata.meta = page.meta
    if path == 'list_qs':
        qs_highlight = request.args.get('q', None)
        if qs_highlight is not None:
            g.pdata.last_qs = g.redis.files.get_file(qs_highlight)
        g.pdata.qs_list = g.redis.files.get_files_list()
    return render_template(template, page=page)
