from flask import Blueprint, render_template
from app.utils.fetch_metar import fetch_all_metar

web = Blueprint('web', __name__)

@web.route('/')
def home():
    return render_template('index.html')

