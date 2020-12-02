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

import dashboard.tools.accounts_handler as accounts_handler
users_db = accounts_handler.accounts_handler()

bp = Blueprint("dash", __name__, url_prefix="/account")

@bp.before_app_request
def load_logged_in_user():
    uname = session.get("username")

    if uname is None:
        g.user = None
        g.uuid = None
    else:
        g.user = uname
        g.uuid = users_db.getUUIDFromUsername(uname)

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view

@bp.route("/dashboard", methods=["GET"])
@login_required
def page_dashboard():
    return render_template("dash/dashboard.html", title="Dashboard", username=g.user)

@bp.route("/schema", methods=["GET"])
@login_required
def page_schema():
    return render_template("dash/schema.html", title="Schema", api_key=g.uuid)


@bp.route("/analytics", methods=["GET"])
@login_required
def page_analytics():
    pass

