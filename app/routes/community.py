from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import mongo

bp = Blueprint('community', __name__)

@bp.route('/')
def index():
    return render_template('community/index.html') 