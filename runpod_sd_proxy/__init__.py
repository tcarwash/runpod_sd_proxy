from flask import Flask
import sqlite3
import logging
import sys
import os

logger = logging.getLogger(__name__)
if os.environ.get("DEBUG"):
    logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
app = Flask(__name__)
db = sqlite3.connect("/data/runpod_sd_proxy.db", check_same_thread=False)
cur = db.cursor()
cur.execute("DROP TABLE IF EXISTS model;")
cur.execute(
    """
    CREATE TABLE model (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    use_model TEXT NOT NULL DEFAULT 'v1-5-pruned-emaonly'
    );
    """
)
test = cur.execute("INSERT INTO model (use_model) VALUES ('v1-5-pruned-emaonly');")
use_model = cur.lastrowid

from .app import app
