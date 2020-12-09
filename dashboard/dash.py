import functools
import os
import base64
import redis
import json
import sys
import pandas as pd
import pika
import time
import pickle
import hashlib
from influxdb.exceptions import InfluxDBClientError
import jsonpickle
import io
import csv

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

import dashboard.tools.accounts_handler as accounts_handler
import dashboard.tools.schema_handler as schema_handler
import dashboard.tools.influx_handler as influx_handler
import dashboard.tools.analytics_handler as analytics_handler

users_db = accounts_handler.accounts_handler()
schema_db = schema_handler.schema_handler()
influx_db = influx_handler.influx_handler()
analytics_handler = analytics_handler.analytics_handler()

def num_df_to_js(df, schema=None):
    res_dict = dict()  # store all numeric fields data
    df["ts"] = df.index
    df["ts"] = df.ts.astype(str)

    for k in df.keys():
        if k != "ts" and schema is not None and k in schema and schema[k]['type'] == 'numeric':
            res_dict[k] = df[["ts", k]].dropna().to_dict(orient='split')['data']

    return res_dict

def loc_df_to_js(df, schema=None):
    res_dict = dict()  # store all map fields data
    df["ts"] = df.index
    df["ts"] = df.ts.astype(str)

    for k in df.keys():
        if k != "ts" and schema is not None and k in schema and schema[k]['type'] == 'location':
            temp = df[["ts", k]].dropna().to_dict(orient='split')['data']
            res_dict[k] = [[i[0], float(i[1].split(',')[0]), float(i[1].split(',')[1])] for i in temp]
    
    return res_dict


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
    my_data = []
    my_map_data = {}

    if len(my_schema) > 0:
        try:
            my_df = influx_db.getDatafromUUID(g.uuid)
            my_data = num_df_to_js(my_df, my_schema)
            my_map_data = loc_df_to_js(my_df, my_schema)
        except InfluxDBClientError:
            pass # no entries in the database


    return render_template(
        "dash/dashboard.html", 
        title="Dashboard", 
        username=g.user,
        my_schema=my_schema,
        my_data=my_data,
        my_map_data=my_map_data
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

@bp.route("/analytics", methods=["GET", "POST"])
@login_required
def page_analytics():
    my_schema = schema_db.getSchemaFromUUID(g.uuid)

    # (2): get the uuid-jobids - organize the accordion - this is chronological order
    # (3): get the uuid-results - do list comprehension on previous jobids
    # (4): get the uuid-requests -    [-do-]

    user_jobs    = list(filter(lambda x: x is not None, analytics_handler.get_jobids_from_uuid(g.uuid)))
    user_reqs    = []
    user_results = []

    for jid in user_jobs:
        user_reqs.append(analytics_handler.get_job_request_from_jobid(jid))

        t = analytics_handler.get_results_for_job(jid)
        if t is not None:
            user_results.append(list(map(
                lambda x: base64.b64encode(x.getvalue()).decode(), t
                )
            ))
        else:
            user_results.append(None)

    # template rendering
    # NOTE: (to future self, I am sorry!) terrible processing model!

    return render_template(
        "dash/analytics.html", 
        title="Analytics", 
        api_key=g.uuid,
        my_schema=my_schema,
        user_results=user_results,
        user_reqs=user_reqs
    )

def generate_job_id(aux_data=""):
    m = hashlib.new('ripemd160')
    m.update(bytes(g.uuid + str(time.time()) + aux_data, encoding="utf-8"))
    return m.hexdigest()

@bp.route("/process/<event_id>", methods=["GET", "POST"])
@login_required
def analytics_request_processor(event_id):

    df = influx_db.getDatafromUUID(g.uuid)

    if event_id == 'export':
        param_fields = request.form.getlist('exportFieldsSel')
        param_filename = request.form['exportInputFilename']
        param_filetype = request.form['exportInputFormat']

        subdf = df[param_fields]

        # source: https://stackoverflow.com/questions/35710361/python-flask-send-file-stringio-blank-files
        if param_filetype == "CSV":
            param_filename += ".csv"
            proxy = io.StringIO()
            subdf.to_csv(proxy, encoding="utf-8")
            mem = io.BytesIO()
            mem.write(proxy.getvalue().encode('utf-8'))
            mem.seek(0)
            proxy.close()

            return send_file(mem, attachment_filename=param_filename, mimetype='text/csv', as_attachment=True)

        elif param_filetype == "JSON":
            param_filename += ".json"
            proxy = io.StringIO()
            proxy.write(subdf.to_json(indent=4))
            mem = io.BytesIO()
            mem.write(proxy.getvalue().encode('utf-8'))
            mem.seek(0)
            proxy.close()

            return send_file(mem, attachment_filename=param_filename, mimetype='application/json', as_attachment=True)

    elif event_id == 'moving_average':
        param_fields = request.form.getlist('stat1FieldsSel')
        param_window = request.form["stat1InputWindowSize"]
        j_id = generate_job_id(event_id)

        r = {
                "data"  : df,
                "params": { "fields": param_fields, "window": param_window },
                "op"    : event_id,
                "job_id": j_id,
                "ts": time.asctime()
        }
        
        x = io.BytesIO()
        pickle.dump(r, x, pickle.HIGHEST_PROTOCOL)
        x.seek(0)

        analytics_handler.send_msg_to_queue(data=x)

        del r["data"] # overloading data (unncessary)
        analytics_handler.store_job_request(uuid=g.uuid, jobid=j_id, jobdesc=jsonpickle.encode(r))

        return redirect(url_for('dash.page_analytics'))