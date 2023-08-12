from __future__ import annotations

from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "<h1>WhatsApp Chat Analyzer</h1>"
