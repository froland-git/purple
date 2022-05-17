from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth # import blueprint from ./__init__.py
from ..models import User
from .forms import LoginForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): # validate_on_submit() from Flask-WTF
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data) # login_user() from Flak-Login
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required # login_required() from Flak-Login
def logout():
    logout_user() # logout_user() from Flak-Login
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
