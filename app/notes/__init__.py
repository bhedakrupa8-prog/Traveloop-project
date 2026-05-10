from flask import Blueprint

notes_bp = Blueprint('notes', __name__, template_folder='../templates/notes')

from app.notes import routes
from app.notes.utils import simple_markdown_to_html

@notes_bp.app_template_filter('markdown')
def markdown_filter(text):
    return simple_markdown_to_html(text)
