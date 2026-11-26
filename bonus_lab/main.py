import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, render_template, request
from processing import (
    TEXTURE_NAMES,
    build_dikan_mesh,
    compute_transformation,
    generate_procedural_texture,
    process_uploaded_texture,
)

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

_MESH = build_dikan_mesh()
_TEXTURES = {
    key: generate_procedural_texture(key, size=256)
    for key in TEXTURE_NAMES
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/mesh", methods=["GET"])
def api_mesh():
    return jsonify({
        "status": "success",
        "mesh": _MESH,
        "textures": [
            {"key": k, "name": label, "data_url": _TEXTURES[k]}
            for k, label in TEXTURE_NAMES.items()
        ],
    })


@app.route("/api/transform", methods=["POST"])
def api_transform():
    try:
        data = request.get_json(force=True) or {}
        result = compute_transformation(data, _MESH["vertices"])
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/upload-texture", methods=["POST"])
def api_upload_texture():
    try:
        if "file" not in request.files or not request.files["file"].filename:
            return jsonify({"error": "Файл не выбран"}), 400
        file = request.files["file"]
        data_url = process_uploaded_texture(file.read())
        return jsonify({
            "status": "success",
            "name": file.filename,
            "data_url": data_url,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5004)
