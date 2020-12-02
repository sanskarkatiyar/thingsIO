# most chunk of code below has been adapted as-is from the flask blog tutorial
# with minor modifications for database access

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

# TODO: add database, message queue access
import dashboard.tools.accounts_handler as accounts_handler
# import . tools.mq_handler as mq

users_db = accounts_handler.accounts_handler()

bp = Blueprint("auth", __name__, url_prefix="/auth")

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    uname = session.get("username")

    if uname is None:
        g.user = None
        g.uuid = None
    else:
        g.user = uname
        g.uuid = users_db.getUUIDFromUsername(uname)


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        username = request.form["inputUsername"]
        password = request.form["inputPassword"]
        error = None

        if not username:
            error = "inputEmpty"
        elif not password:
            error = "inputEmpty."
        elif users_db.isExistingUsername(username):
            error = "usernameExists"

        if error is None:
            users_db.addUser(username, generate_password_hash(password))
            error = "success"

            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Log in a registered user by adding the user id to the session."""

    if request.method == "POST":
        username = request.form["inputUsername"]
        password = request.form["inputPassword"]

        error = None

        user_ = username if users_db.isExistingUsername(username) else None
        pass_ = None

        if (not username) or (not password) or (user_ is None):
            error = "invalidCredentials"
        else:
            pass_ = users_db.getPasswordHashFromUsername(user_)
            if not check_password_hash(pass_, password):
                error = "invalidCredentials"

        if error is None:
            session.clear()
            session["username"] = username # NOTE: maybe something alias id, for security?

            return redirect(url_for("dash.page_dashboard"))

        flash(error)

    return render_template("auth/login.html")

@bp.route("/logout", methods=["GET"])
@login_required
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    g.user = None
    g.uuid = None
    return redirect(url_for("auth.login"))