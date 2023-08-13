from __future__ import annotations

import hashlib
import os
import zipfile

import dotenv
from flask import flash
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import select_autoescape

from src.data import etl
from src.data import s3
from src.utils import files

_ = dotenv.load_dotenv(dotenv.find_dotenv())

app = Flask(__name__)
app.secret_key = os.environ.get(
    "APP_SECRET_KEY",
    os.urandom(16).hex(),
)


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

        if not files.allowed_file(file.filename):
            flash("Invalid file type")
            return redirect(request.url)

        s3_filename = s3.upload_to_s3(
            file,
            files.unique_filename_generator(file.filename, file),
        )
        if not s3_filename:
            flash("Error occurred while uploading to S3.")
            return redirect(request.url)
        # WIP
        # if filename.endswith(".zip"):
        #     # If your file is a zip, and you still need to convert it to txt,
        #     # you'll need to handle this part differently as the file is no longer on your server.
        #     # Consider downloading it from S3, converting it, then re-uploading.
        #     flash("ZIP file uploads need additional handling.")
        #     return redirect(request.url)
        return redirect(
            url_for("analyze", upload_filename=s3_filename, _external=True),
        )
    return render_template("index.html")


@app.route("/analyze/<upload_filename>", methods=["GET", "POST"])
def analyze(upload_filename: str):
    db = etl.etl_pipeline(os.path.join(app.config["UPLOAD_FOLDER"], upload_filename))

    query = ""
    keyword = ""
    page = request.args.get("page", 1, type=int)

    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        strict_search = request.form.get("strict_search") == "true"

        if strict_search:
            query = f"SELECT * FROM chat_history WHERE message = '{keyword}'"
        else:
            query = f"SELECT * FROM chat_history WHERE message LIKE '%{keyword}%'"

        total_results = db.sql(
            f"""
                               SELECT COUNT(*)
                               FROM ({query}) AS foo""",
        ).fetchone()[0]
        results = db.sql(
            f"""
                         SELECT *
                         FROM ({query}) AS foo
                         LIMIT 20 OFFSET {(page - 1) * 20}""",
        ).fetchall()
        top_senders = db.sql(
            f"""
                        SELECT sender, COUNT(*) as count
                        FROM ({query}) AS foo
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
        keyword=keyword,
        page=page,
        top_senders=top_senders,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
