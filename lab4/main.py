import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from processing import clip_midpoint, clip_cyrus_beck, parse_input_file
import time

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    try:
        content = request.get_json(force=True).get("content", "")
        return jsonify({"status": "success", "data": parse_input_file(content)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/clip", methods=["POST"])
def clip():
    try:
        t0 = time.perf_counter()
        data = request.get_json(force=True)
        algo = data.get("algorithm", "midpoint")
        segments = data.get("segments", [])
        w = data.get("window", {"xmin": -10, "ymin": -10, "xmax": 10, "ymax": 10})
        poly = data.get("polygon")

        results = []
        for s in segments:
            if algo == "cyrus_beck":
                target_poly = poly if poly else [
                    [w["xmin"], w["ymin"]],
                    [w["xmax"], w["ymin"]],
                    [w["xmax"], w["ymax"]],
                    [w["xmin"], w["ymax"]]
                ]
                res = clip_cyrus_beck(s["x1"], s["y1"], s["x2"], s["y2"], target_poly)
            else:
                res = clip_midpoint(s["x1"], s["y1"], s["x2"], s["y2"], w["xmin"], w["ymin"], w["xmax"], w["ymax"])
            res["orig"] = [[s["x1"], s["y1"]], [s["x2"], s["y2"]]]
            results.append(res)

        dt = (time.perf_counter() - t0) * 1000.0
        return jsonify({"status": "success", "results": results, "time_ms": round(dt, 4)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5003)
