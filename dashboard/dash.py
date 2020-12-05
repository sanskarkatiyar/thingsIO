import functools
import os
import redis
import json
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
import dashboard.tools.schema_handler as schema_handler

users_db = accounts_handler.accounts_handler()
schema_db = schema_handler.schema_handler()

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
        if g.user is None or g.uuid is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view

@bp.route("/dashboard", methods=["GET"])
@login_required
def page_dashboard():
    return render_template("dash/dashboard.html", title="Dashboard", username=g.user)

@bp.route("/schema", methods=["GET", "POST"])
@login_required
def page_schema():
    schema_update_success = False

    if request.method == "POST":
        schema_json_text = request.form['inputSchema']
        schema_dict = None
        flag = 'schemaUpdate'

        try:
            schema_dict = json.loads(schema_json_text)
        except:
            flag = 'schemaUpdateFail'

        if schema_dict is not None:
            if schema_db.setSchemaForUUID(g.uuid, schema_dict):
                flag = 'schemaUpdateSuccess'
                if schema_db.isValidSchema(schema_dict):
                    flag = 'schemaUpdateFormatFail'
            else:
                flag = 'schemaUpdateFail'

        flash(flag)

    schema_text = json.dumps(schema_db.getSchemaFromUUID(g.uuid), indent=4)
    return render_template(
        "dash/schema.html", 
        title="Schema", 
        api_key=g.uuid, 
        user_schema=schema_text
    )

@bp.route("/analytics", methods=["GET"])
@login_required
def page_analytics():
    pass

