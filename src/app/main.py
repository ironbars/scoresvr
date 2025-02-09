from __future__ import annotations

import base64
import os
import pathlib
import zlib
from typing import TYPE_CHECKING, Any

from flask import Flask, g, jsonify, make_response
from pymongo import MongoClient
from pymongo.database import Database
from werkzeug.middleware.proxy_fix import ProxyFix

if TYPE_CHECKING:
    from flask import Response


MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/music")
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1, x_prefix=1, x_for=2, x_proto=1)


def decode_engraving(eng: list[str]) -> bytes:
    b64str = "".join(eng)
    b64bytes = b64str.encode("utf-8")
    compressed_data = base64.b64decode(b64bytes)
    data = zlib.decompress(compressed_data)

    return data


def get_db() -> Database:
    if "db" not in g:
        client = MongoClient(MONGO_URI)
        g.db = client.get_database()

    return g.db


@app.teardown_appcontext
def close_db(exception) -> None:
    db = g.pop("db", None)

    if db is not None:
        db.client.close()


@app.route("/scores", methods=["GET"])
def get_scores() -> Response:
    db = get_db()
    scores = list(db.scores.find({}, {"_id": 0}))

    return jsonify(scores)


@app.route("/scores/<title>", methods=["GET"])
def get_score(title: str) -> Response | tuple[Response, int]:
    db = get_db()
    score = db.scores.find_one({"simple_name": title})

    if not score:
        return jsonify({"error": "Score not found"}), 404

    engraving = db.engravings.find_one({"_id": score["engraving_id"]})

    if not engraving:
        return jsonify({"error": "Engraving not found"}), 404
    
    try:
        engraving_data = decode_engraving(engraving["engraving"])
    except (KeyError, zlib.error, base64.binascii.Error) as e:
        return jsonify({"error": f"Decoding error: {str(e)}"}), 500

    response = make_response(engraving_data)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={score['title']}.pdf"

    return response


if __name__ == "__main__":
    app.run(debug=True)
