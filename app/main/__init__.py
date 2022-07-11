from flask import Blueprint

# main - constructor
# 'main' - name of Blueprint
main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission


# 'app_context_processor' to avoid adding an extra argument in function render_template()
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
