import pathlib
import os
import base64
import zlib
from typing import Any

from flask import Flask, Blueprint, render_template, make_response
from werkzeug.middleware.proxy_fix import ProxyFix
from pymongo import MongoClient


MONGO_HOST = os.environ.get("SCORESVR_MONGO_HOST", "127.0.0.1")
MONGO_PORT = os.environ.get("SCORESVR_MONGO_PORT", "27017")

scoreserver = Blueprint("scoreserver", __name__, template_folder="templates")
client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
db = client.music


def get_scores() -> list[dict[str, Any]]:
    scores = db.scores.find()

    return scores


def decode_engraving(eng: list[str]) -> bytes:
    b64str = "".join(eng)
    b64bytes = b64str.encode("utf-8")
    compressed_data = base64.b64decode(b64bytes)
    data = zlib.decompress(compressed_data)

    return data


@scoreserver.route("/")
@scoreserver.route("/index/")
def home() -> str:
    scores = get_scores()

    return render_template("index.html", scores=scores)


@scoreserver.route("/scores/<title>")
def send_score(title: str) -> flask.Response:
    score = db.scores.find_one({"simple_name": title})
    engraving = db.engravings.find_one({"_id": score["engraving_id"]})
    engraving_data = decode_engraving(engraving["engraving"])
    response = make_response(engraving_data)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={score['title']}.pdf"

    return response


app = Flask(__name__)
app.register_blueprint(scoreserver)
app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1, x_prefix=1, x_for=2, x_proto=1)
