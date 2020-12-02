import functools
import os
import redis
import sys

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

bp = Blueprint("dashboard", __name__, url_prefix="/account")

@bp.before_app_request
def load_logged_in_user():
    uname = session.get("username")

    if uname is None:
        g.user = None
    else:
        g.user = uname

@bp.route("/dashboard", methods=["GET"])
def page_dashboard():
    return render_template("dashboard/dashboard.html", title="Dashboard", username=g.user)

@bp.route("/schema", methods=["GET"])
def page_schema():
    pass

@bp.route("/analytics", methods=["GET"])
def page_analytics():
    pass

