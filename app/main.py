import pathlib

from flask import Flask, Blueprint, render_template, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

SCORES_PATH = "scores"
scoreserver = Blueprint("scoreserver", __name__, template_folder="templates")


def get_scores():
    scores_path = pathlib.Path(SCORES_PATH)
    scores = [score.name.rstrip(".pdf") for score in scores_path.glob("*.pdf")]

    return scores


@scoreserver.route("/")
@scoreserver.route("/index/")
def home():
    scores = get_scores()

    return render_template("index.html", scores=scores)


# This shouldn't actually be doing anything in most cases.  It is just here to generate
# URLs for the scores themselves.  There might be a better way to do this.
@scoreserver.route("/scores/<title>")
def send_score(title):
    return send_from_directory("scores", title)


app = Flask(__name__)
app.register_blueprint(scoreserver)
app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1, x_prefix=1, x_for=2, x_proto=1)
