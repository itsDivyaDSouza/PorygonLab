from pathlib import Path
from io import BytesIO
import base64

import numpy as np
from flask import Flask, jsonify, render_template, request, send_from_directory
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)

SAMPLES_FOLDER = Path(__file__).parent / "samples"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

MATH_INFO = {
    "brightness": {
        "name": "Brightness",
        "formula": "A_new = clip(A_old + c, 0, 255)",
        "matrix": "R_new = R_old + c\nG_new = G_old + c\nB_new = B_old + c",
        "explanation": "The constant c is added to each pixel value. Values are clipped to the valid 0–255 range.",
    },
    "grayscale": {
        "name": "Grayscale",
        "formula": "A_new = 0.299R_old + 0.587G_old + 0.114B_old",
        "matrix": "[ 0.299   0.587   0.114 ]",
        "explanation": "The red, green, and blue channel matrices are combined using weights to produce grayscale intensity values.",
    },
    "invert": {
        "name": "Invert",
        "formula": "A_new = 255 - A_old",
        "matrix": "R_new = 255 - R_old\nG_new = 255 - G_old\nB_new = 255 - B_old",
        "explanation": "Each pixel value is subtracted from the maximum intensity, 255.",
    },
    "sepia": {
        "name": "Sepia",
        "formula": "x_new = T × x_old",
        "matrix": (
            "T = [ 0.393  0.769  0.189 ]\n"
            "    [ 0.349  0.686  0.168 ]\n"
            "    [ 0.272  0.534  0.131 ]"
        ),
        "explanation": "The transformation matrix T mixes a pixel's RGB values. Here, x_old and x_new are the pixel's RGB column vectors.",
    },
    "rotate": {
        "name": "Rotate 90°",
        "formula": "A_new = P(A_old)",
        "matrix": "P rearranges pixel positions\noutput (x, y) ← input (y, H − 1 − x)",
        "explanation": "The image is rotated clockwise by rearranging its pixel positions.",
    },
    "flip_horizontal": {
        "name": "Flip horizontal",
        "formula": "A_new = P(A_old)",
        "matrix": "P rearranges pixel positions\noutput (x, y) ← input (W − 1 − x, y)",
        "explanation": "The pixel columns are reversed, reflecting the image across a vertical axis.",
    },
    "flip_vertical": {
        "name": "Flip vertical",
        "formula": "A_new = P(A_old)",
        "matrix": "P rearranges pixel positions\noutput (x, y) ← input (x, H − 1 − y)",
        "explanation": "The pixel rows are reversed, reflecting the image across a horizontal axis.",
    },
}


@app.route("/")
def home():
    sample_files = []

    if SAMPLES_FOLDER.exists():
        sample_files = sorted(
            path.name
            for path in SAMPLES_FOLDER.iterdir()
            if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS
        )

    return render_template("index.html", sample_files=sample_files)


@app.route("/samples/<path:filename>")
def sample_image(filename):
    safe_filename = secure_filename(filename)
    return send_from_directory(SAMPLES_FOLDER, safe_filename)


@app.route("/process", methods=["POST"])
def process_image():
    uploaded_file = request.files.get("image")
    operation = request.form.get("operation")

    if uploaded_file is None:
        return jsonify({"error": "No image was received. Choose an image again."}), 400

    if operation not in MATH_INFO:
        return jsonify({"error": "Choose a valid operation."}), 400

    try:
        image = Image.open(uploaded_file.stream).convert("RGB")
        pixels = np.array(image, dtype=np.float32)
        amount = int(request.form.get("amount", "30"))
    except Exception as error:
        return jsonify({"error": f"Could not open the image: {error}"}), 400

    if operation == "brightness":
        result = np.clip(pixels + amount, 0, 255)

    elif operation == "grayscale":
        gray = (
            0.299 * pixels[:, :, 0]
            + 0.587 * pixels[:, :, 1]
            + 0.114 * pixels[:, :, 2]
        )
        result = np.stack((gray, gray, gray), axis=2)

    elif operation == "invert":
        result = 255 - pixels

    elif operation == "sepia":
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131],
        ])
        result = np.clip(pixels @ sepia_matrix.T, 0, 255)

    elif operation == "rotate":
        result = np.rot90(pixels, k=3, axes=(0, 1))

    elif operation == "flip_horizontal":
        result = np.flip(pixels, axis=1)

    else:  # flip_vertical
        result = np.flip(pixels, axis=0)

    # Compare a 4×4 red-channel sample from the input and output.
    # For grayscale, the output sample contains grayscale intensity values.
    old_matrix = np.clip(pixels[:4, :4, 0], 0, 255).astype(int).tolist()
    new_matrix = np.clip(result[:4, :4, 0], 0, 255).astype(int).tolist()

    result_image = Image.fromarray(
        np.clip(result, 0, 255).astype(np.uint8)
    )

    output = BytesIO()
    result_image.save(output, format="PNG")
    encoded_image = base64.b64encode(output.getvalue()).decode("utf-8")

    return jsonify({
        "image": f"data:image/png;base64,{encoded_image}",
        "math": MATH_INFO[operation],
        "matrix": MATH_INFO[operation]["matrix"],
        "operation": operation,
        "old_matrix": old_matrix,
        "new_matrix": new_matrix,
        "width": result_image.width,
        "height": result_image.height,
    })


if __name__ == "__main__":
    app.run(debug=True)