from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth # import blueprint from ./__init__.py
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm
from .. import db
from ..email import send_email

#----- [08e] Actions for unconfirmed users START-----
# use decorator before_app_request()
@auth.before_app_request
def before_request():
    # is_authenticated - https://flask-login.readthedocs.io/en/latest/
    #     # current_user.confirmed - from model.py
    #     # request.endpoint - https://stackoverflow.com/questions/19261833/what-is-an-endpoint-in-flask
    #     # request.endpoint should be out of blueprint 'auth'
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
#----- [08e] Actions for unconfirmed users END-----

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): # validate_on_submit() from Flask-WTF
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data) # login_user() from Flask-Login
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required # login_required() from Flak-Login
def logout():
    logout_user() # logout_user() from Flak-Login
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(user)
        #-----[08e] Block for sending email confirmation-----
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
        #-----[08e] End block-----
    return render_template('auth/register.html', form=form)

#----- [08e] Function to confirm account -----
@auth.route('/confirm/<token>')
@login_required # Decorator form Flask-Login. Need to login on a first step
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

#----- [08e] Function to resend confirmation email -----
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

#----- [08f] Function to change password for existing user -----
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Use def verify_password(self, password) form models.py as a condition
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data  # password - property from models.py
            db.session.add(current_user)  # Only add it to the session without commit (because session is still open)
            # db.session.commit() # but with commit it is still working
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)  # shows which form to display