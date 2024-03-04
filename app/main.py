import pathlib

from flask import Flask, Blueprint, render_template, send_from_directory

SCORES_PATH = "scores"
scoreserver = Blueprint("scoreserver", __name__, template_folder="templates")


def get_scores():
    scores_path = pathlib.Path(SCORES_PATH)
    scores = [
        score.name.rstrip(".pdf")
        for score in scores_path.glob("*.pdf")
    ]

    return scores


@scoreserver.route("/")
@scoreserver.route("/index/")
def home():
    scores = get_scores()

    return render_template("index.html", scores=scores)

@scoreserver.route("/scores/<title>")
def send_score(title):
    return send_from_directory('scores', title)


app = Flask(__name__)
app.register_blueprint(scoreserver, url_prefix="/scoreserver")
