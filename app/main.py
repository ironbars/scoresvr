import pathlib

from flask import Flask, render_template

app = Flask(__name__)

SCORES_PATH = "static"

def get_scores():
    scores_path = pathlib.Path(SCORES_PATH)
    scores = []

    for s in scores_path.iterdir():
        if s.is_file and s.name.endswith(".pdf"):
            scores.append(s.name.rstrip(".pdf"))

    return scores


@app.route("/")
@app.route("/index/")
def home():
    scores = get_scores()

    return render_template("index.html", path=SCORES_PATH, scores=scores)

