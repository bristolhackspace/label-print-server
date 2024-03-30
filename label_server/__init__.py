from flask import Flask, request, redirect
from .label_print import print_label
import requests
import logging

app = Flask(__name__, instance_relative_config=True)
logger = logging.Logger(__name__)

app.config.from_pyfile('config.py', silent=True)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

@app.route("/print")
def _print():
    label_id = request.args.get("id")
    return_url = request.args.get("return_url")
    try:
        membership_url = app.config["MEMBERSHIP_URL"]
        r = requests.get(f'{membership_url}/api/labels/label/{label_id}')
        label_data = r.json()
        serial = label_data.get("id")
        name = label_data.get("name", "")
        expiry = label_data.get("expiry", "who knows?")
        caption = label_data.get("caption", "Invalid")

        cut = True
        print_label(name, caption, expiry, serial, cut)
    except Exception as ex:
        logger.exception("Error printing label")
    return redirect(return_url)