from flask import render_template
from . import main


@main.app_errorhandler(404) # Use decorator app_errorhandler instead of errorhandler
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
