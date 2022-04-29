from flask import Blueprint

# main - constructor
# 'main' - name of Blueprint
main = Blueprint('main', __name__)

from . import views, errors
