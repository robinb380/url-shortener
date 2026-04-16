from flask import Flask, redirect, request, jsonify
import random
import string
from urllib.parse import urlparse
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)



def init_db():
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            code TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            clicks INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

init_db()

def generate_code():
    """
    Generates a random 6-character code using letters and digits.
    This will be used as the short URL identifier.
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))


def is_valid_url(url):
    """
    Validates that the URL has a correct structure.
    Only allows http and https URLs with a valid domain.
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ["http", "https"] and parsed.netloc
    except:
        return False


@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    if not is_valid_url(original_url):
        return jsonify({"error": "Invalid URL format"}), 400

    code = generate_code()

    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    # ensure unique code
    cursor.execute("SELECT code FROM urls WHERE code = ?", (code,))
    while cursor.fetchone():
        code = generate_code()
        cursor.execute("SELECT code FROM urls WHERE code = ?", (code,))

    cursor.execute(
        "INSERT INTO urls (code, original_url, clicks) VALUES (?, ?, ?)",
        (code, original_url, 0)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "code": code,
        "short_url": f"http://localhost:8080/{code}"
    })


@app.route("/<code>")
def resolve(code):
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    cursor.execute("SELECT original_url, clicks FROM urls WHERE code = ?", (code,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "Link not found"}), 404

    original_url, clicks = row

    # update clicks
    cursor.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE code = ?",
        (code,)
    )

    conn.commit()
    conn.close()

    return redirect(original_url)

@app.route("/stats/<code>")
def get_stats(code):
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT original_url, clicks FROM urls WHERE code = ?",
        (code,)
    )
    row = cursor.fetchone()

    conn.close()

    if not row:
        return jsonify({"error": "Code not found"}), 404

    original_url, clicks = row

    return jsonify({
        "code": code,
        "original_url": original_url,
        "clicks": clicks
    })

if __name__ == "__main__":
    app.run(debug=True, port=8080)