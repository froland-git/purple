from flask import render_template
from . import auth # import blueprint from ./__init__.py


@auth.route('/login')
def login():
    return render_template('auth/login.html')
