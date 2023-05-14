import pathlib

from flask import Flask, render_template

app = Flask(__name__)

SCORES_PATH = "scores"

def get_scores():
    scores_path = pathlib.Path(SCORES_PATH)
    scores = [
        score.name.rstrip(".pdf")
        for score in scores_path.glob("*.pdf")
    ]

    return scores


@app.route("/")
@app.route("/index/")
def home():
    scores = get_scores()

    return render_template("index.html", scores=scores)

@app.route("/scores/<title>")
def score_getter(title):
    return f"{title}"
