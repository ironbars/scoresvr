from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from bson.errors import InvalidId
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import Flask, Response, g, jsonify, make_response, request
from gridfs import GridFS
from pymongo import MongoClient
from werkzeug.middleware.proxy_fix import ProxyFix

if TYPE_CHECKING:
    from pymongo.database import Database


MONGO_URI = os.getenv("MONGO_URI", "")
app = Flask(__name__)
app.url_map.strict_slashes = False
app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1, x_prefix=1, x_for=2, x_proto=1)  # type: ignore[method-assign]


def get_db() -> Database:
    if "db" not in g:
        client: MongoClient = MongoClient(MONGO_URI)
        g.db = client.get_database()

    return g.db


def build_scores_query(args: dict[str, list[str]]) -> dict[str, Any]:
    query: dict[str, Any] = dict()

    for key, value in args.items():
        if len(value) > 1:
            query[key] = {"$in": value}
        else:
            single_value = value[0]
            if key == "_id":
                try:
                    query[key] = ObjectId(single_value)
                except InvalidId:
                    continue  # ignore invalid ObjectId
            else:
                query[key] = single_value

    return query


@app.teardown_appcontext
def close_db(exception) -> None:
    db = g.pop("db", None)

    if db is not None:
        db.client.close()


@app.route("/scores", methods=["GET"])
def get_scores() -> Response:
    db = get_db()
    query = build_scores_query(request.args.to_dict(flat=False))
    scores = list(db.scores.find(query))

    return Response(dumps(scores), mimetype="application/json")


@app.route("/scores/<title>", methods=["GET"])
def get_score(title: str) -> Response | tuple[Response, int]:
    db = get_db()
    score = db.scores.find_one({"simple_name": title})

    if not score:
        return jsonify({"error": "Score not found"}), 404

    fs = GridFS(db)
    engraving_data = fs.get(score["engraving_id"]).read()
    response = make_response(engraving_data)

    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={score['title']}.pdf"

    return response


if __name__ == "__main__":
    app.run(debug=True)
