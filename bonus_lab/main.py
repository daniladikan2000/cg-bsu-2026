import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, render_template, request, send_from_directory
from processing import (
    build_dikan_mesh,
    compute_transformation,
    load_textures_from_dir,
    process_uploaded_texture,
)

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

TEXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")
_MESH = build_dikan_mesh()
_TEXTURES = load_textures_from_dir(TEXTURES_DIR)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/mesh", methods=["GET"])
def api_mesh():
    return jsonify({
        "status": "success",
        "mesh": _MESH,
        "textures": _TEXTURES,
    })


@app.route("/api/textures/<filename>", methods=["GET"])
def api_texture_file(filename):
    return send_from_directory(TEXTURES_DIR, filename)


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
