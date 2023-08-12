from __future__ import annotations

import hashlib
import os
import zipfile

from flask import flash
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import select_autoescape
from werkzeug.utils import secure_filename

from src.data import etl

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


def md5_filter(s, _=None):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


env = Environment(
    loader=FileSystemLoader(searchpath="templates"),
    autoescape=select_autoescape(["html", "xml"]),
)
env.filters["hash"] = md5_filter
app.jinja_env.filters["hash"] = md5_filter


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


@app.route("/analyze/<upload_filename>", methods=["GET"])
def analyze(upload_filename: str):
    db = etl.etl_pipeline(os.path.join(app.config["UPLOAD_FOLDER"], upload_filename))

    query = request.args.get("query", "").strip()
    page = request.args.get("page", 1, type=int)

    if query:
        total_results = db.sql(
            f"""
                               SELECT COUNT(*)
                               FROM chat_history
                               WHERE LOWER(message) LIKE '%{query.lower()}%'""",
        ).fetchone()[0]
        results = db.sql(
            f"""
                         SELECT *
                         FROM chat_history
                         WHERE LOWER(message) LIKE '%{query.lower()}%'
                         LIMIT 20 OFFSET {(page - 1) * 20}""",
        ).fetchall()
        top_senders = db.sql(
            f"""
                        SELECT sender, COUNT(*) as count
                        FROM chat_history
                        WHERE LOWER(message) LIKE '%{query.lower()}%'
                        GROUP BY sender
                        ORDER BY count DESC
                        LIMIT 3""",
        ).fetchall()
    else:
        results = db.sql("SELECT * FROM chat_history LIMIT 10").fetchall()
        top_senders = db.sql(
            "SELECT sender, COUNT(*) as count FROM chat_history GROUP BY sender ORDER BY count DESC LIMIT 3",
        ).fetchall()
        total_results = 10

    return render_template(
        "analyze.html",
        uploaded_filename=upload_filename,
        results=results,
        total_results=total_results,
        query=query,
        page=page,
        top_senders=top_senders,
    )
