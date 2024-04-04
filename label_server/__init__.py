from flask import Flask, request, redirect, Response
from werkzeug.exceptions import HTTPException
from .label_print import print_label
import logging


app = Flask(__name__, instance_relative_config=True)
logger = logging.Logger(__name__)

app.config.from_pyfile('config.py', silent=True)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

@app.errorhandler(Exception)
def all_exception_handler(error):
    if isinstance(error, HTTPException):
        return error

    res = {"error": str(error)}
    return res, 500


@app.route("/print", methods=["POST", "OPTIONS"])
def _print():
    if request.method == "OPTIONS":
        return {}

    label_data = request.get_json()
    serial = label_data.get("id")
    name = label_data.get("name", "")
    expiry = label_data.get("expiry", "who knows?")
    caption = label_data.get("caption", "Invalid")

    cut = True
    try:
        print_label(name, caption, expiry, serial, cut)
    except FileNotFoundError:
        return {"error": "Printer not switched on"}, 500

    return {"success": True}

@app.after_request
def add_origin(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "origin, content-type, accept"
    return response