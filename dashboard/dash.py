import functools
import os
import redis
import json
import sys
import pandas as pd

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
import dashboard.tools.influx_handler as influx_handler

users_db = accounts_handler.accounts_handler()
schema_db = schema_handler.schema_handler()
influx_db = influx_handler.influx_handler()

def num_df_to_js(df, schema=None):
    res_dict = dict()  # store all numeric fields data
    df["ts"] = df.index
    df["ts"] = df.ts.astype(str)

    for k in df.keys():
        if k != "ts" and schema is not None and schema[k]['type'] == 'numeric':
            res_dict[k] = df[["ts", k]].to_dict(orient='split')['data']

    return res_dict

def loc_df_to_js(df, schema):
    # TODO: location data 
    raise NotImplementedError


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
    my_schema = schema_db.getSchemaFromUUID(g.uuid)
    my_schema_text = json.dumps(my_schema, indent=4)
    my_data = []
    if len(my_schema_text) > 0:
        my_df = influx_db.getDatafromUUID(g.uuid)
        my_data = num_df_to_js(my_df, my_schema)

    return render_template(
        "dash/dashboard.html", 
        title="Dashboard", 
        username=g.user,
        my_schema=my_schema,
        my_data=my_data
    )

@bp.route("/schema", methods=["GET", "POST"])
@login_required
def page_schema():
    if request.method == "POST":
        schema_json_text = request.form['inputSchema']
        schema_dict = None
        flag = 'schemaUpdate'

        try:
            schema_dict = json.loads(schema_json_text)
        except:
            flag = 'schemaUpdateFail'

        if schema_dict is not None and schema_db.isValidSchema(schema_dict):
            if schema_db.setSchemaForUUID(g.uuid, schema_dict):
                flag = 'schemaUpdateSuccess'
        else:
            flag = 'schemaUpdateFail'

        flash(flag)

    schema_text = json.dumps(schema_db.getSchemaFromUUID(g.uuid), indent=4)
    return render_template(
        "dash/schema.html", 
        title="Schema", 
        api_key=g.uuid, 
        my_schema=schema_text
    )

@bp.route("/analytics", methods=["GET"])
@login_required
def page_analytics():
    pass

