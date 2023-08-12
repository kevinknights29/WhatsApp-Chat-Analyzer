from __future__ import annotations

import os

from flask import flash
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {"zip", "txt"}

app = Flask(__name__)
app.secret_key = os.urandom(16).hex()
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "chatFile" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["chatFile"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(
                url_for("analyze", upload_filename=filename, _external=True),
            )
    return render_template("index.html")


@app.route("/analyze/<upload_filename>")
def analyze(upload_filename: str):
    return render_template("analyze.html", uploaded_filename=upload_filename)
