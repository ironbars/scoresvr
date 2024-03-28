import json
import base64
import re
import zlib
import os
from pathlib import Path

from bson.objectid import ObjectId


SCORES_DIR = Path(os.environ.get("SCORESVR_SCORES_DIR", ""))
METADATA_RE = re.compile(r"\s+\\?(title|subtitle|composer|time|key)(\s+=)?\s+(.*)")


def get_score_metadata(name: str, files: list[str | Path]) -> dict[str, str]:
    metadata = dict([("_id", str(ObjectId()))])
    metadata["simple_name"] = name

    for f in files:
        with open(f, "r") as src:
            for line in src:
                if (match := METADATA_RE.match(line)) is not None:
                    key = match.group(1)
                    value = match.group(3).strip().strip('"')

                    if key in metadata:
                        try:
                            metadata[key].append(value)
                        except AttributeError:
                            metadata[key] = [metadata[key], value]
                    else:
                        metadata[key] = value

    try:
        metadata["key"] = metadata["key"].replace("\\", "").title()
    except AttributeError:
        for i, mkey in enumerate(metadata["key"]):
            metadata["key"][i] = mkey.replace("\\", "").title()

    return metadata


def get_score_data(filename: str | Path) -> list[str]:
    with open(filename, "rb") as pdf:
        data = pdf.read()

    compressed = zlib.compress(data)
    score_bytes = base64.encodebytes(compressed)
    score_str = score_bytes.decode("utf-8")
    score_seq = score_str.splitlines()

    return score_seq


def main():
    src_dir = SCORES_DIR / "src"
    score_sources = [d for d in src_dir.iterdir() if d.stem != "with-fingering"]
    metadata = list()
    data = list()

    for score_dir in score_sources:
        simple_name = score_dir.stem
        src_files = score_dir.glob("**/*.ly")

        metadata.append(get_score_metadata(simple_name, src_files))

    for score in SCORES_DIR.glob("*.pdf"):
        engraving = get_score_data(score)
        score_data = dict([("_id", str(ObjectId()))])
        score_data["engraving"] = engraving

        for meta in metadata:
            if score.stem == meta["title"]:
                meta["engraving_id"] = score_data["_id"]
                score_data["score_id"] = meta["_id"]
                data.append(score_data)

    scores = dict([("scores", metadata)])
    engravings = dict([("engravings", data)])

    with open("scores.json", "w", encoding="utf-8") as db:
        json.dump(scores, db, ensure_ascii=False, indent=2)

    with open("engravings.json", "w") as eng_db:
        json.dump(engravings, eng_db, indent=2)


if __name__ == "__main__":
    main()
