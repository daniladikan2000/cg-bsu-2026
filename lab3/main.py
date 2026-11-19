import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from processing import rasterize

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/rasterize", methods=["POST"])
def api_rasterize():
    try:
        data = request.get_json(force=True)
        algo = data.get("algorithm", "bresenham")
        params = {
            "x1": int(data.get("x1", 1)),
            "y1": int(data.get("y1", 1)),
            "x2": int(data.get("x2", 14)),
            "y2": int(data.get("y2", 7)),
            "xc": int(data.get("xc", 0)),
            "yc": int(data.get("yc", 0)),
            "r": int(data.get("r", 8))
        }
        res = rasterize(algo, params)
        return jsonify({"status": "success", "data": res})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5002)
