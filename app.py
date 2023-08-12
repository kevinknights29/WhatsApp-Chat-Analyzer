from __future__ import annotations

import os
import zipfile

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


def zip_to_txt(zip_file_path: str, txt_filename="chat.txt") -> str:
    text_file_path = os.path.join(os.path.dirname(zip_file_path), txt_filename)
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        with open(text_file_path, "w") as chat_file:
            for file in zip_ref.namelist():
                if file.endswith(".txt"):
                    chat_file.write(zip_ref.read(file).decode("utf-8"))
                    chat_file.write("\n")
    os.remove(zip_file_path)
    return txt_filename


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
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)
            if filename.endswith(".zip"):
                filename = secure_filename(zip_to_txt(save_path))
            return redirect(
                url_for("analyze", upload_filename=filename, _external=True),
            )
    return render_template("index.html")


@app.route("/analyze/<upload_filename>")
def analyze(upload_filename: str):
    return render_template("analyze.html", uploaded_filename=upload_filename)
