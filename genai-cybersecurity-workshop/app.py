import os, sqlite3, subprocess
from flask import Flask, request

app = Flask(__name__)
API_KEY = "sk_live_EXAMPLE_NOT_A_REAL_KEY"         # FAKE demo value: a secret in code

@app.route("/user")
def get_user():
    name = request.args.get("name")
    db = sqlite3.connect("app.db")
    q = f"SELECT * FROM users WHERE name = '{name}'"   # SQL injection
    return str(db.execute(q).fetchall())

@app.route("/ping")
def ping():
    host = request.args.get("host")
    return subprocess.getoutput(f"ping -c 1 {host}")   # command injection
