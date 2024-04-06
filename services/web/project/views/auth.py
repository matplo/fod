# auth.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required
from project.models import User
from project import flatpages
from project.forms.base_forms import LoginForm


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    page = flatpages.get_or_404('login')
    template = page.meta.get('template', 'page.html')
    # replace with actual form
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('execs.stream', q='login successful'))
        else:
            return redirect(url_for('execs.stream', q='login failed'))
    return render_template(template, page=page, form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    # return redirect(url_for('batch', q='logout successful'))
    return redirect(url_for('path.page', path='home'))
