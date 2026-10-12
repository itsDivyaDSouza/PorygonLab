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

OPERATIONS = {
    "brightness": "Brightness",
    "grayscale": "Grayscale",
    "invert": "Invert",
    "rotate": "Rotate 90°",
    "flip_horizontal": "Flip horizontal",
    "flip_vertical": "Flip vertical",
}


def rgb_text(pixel):
    values = np.clip(np.rint(pixel), 0, 255).astype(int).tolist()
    return f"({values[0]}, {values[1]}, {values[2]})"


def rotate_90(pixels, direction):
    if direction == "counterclockwise":
        return np.rot90(pixels, k=1, axes=(0, 1)).copy()
    return np.rot90(pixels, k=3, axes=(0, 1)).copy()


def build_step(operation, before, after, amount, before_size, after_size, sample_position, direction):
    height, width = before.shape[:2]
    x, y = sample_position
    old_pixel = before[y, x]
    new_height, new_width = after.shape[:2]
    if operation == "rotate":
        if direction == "counterclockwise":
            mapped_x, mapped_y = y, width - 1 - x
        else:
            mapped_x, mapped_y = height - 1 - y, x
        new_pixel = after[mapped_y, mapped_x]
    elif operation == "flip_horizontal":
        mapped_x, mapped_y = width - 1 - x, y
        new_pixel = after[mapped_y, mapped_x]
    elif operation == "flip_vertical":
        mapped_x, mapped_y = x, height - 1 - y
        new_pixel = after[mapped_y, mapped_x]
    else:
        mapped_x, mapped_y = x, y
        new_pixel = after[mapped_y, mapped_x]
    old_rgb = np.clip(np.rint(old_pixel), 0, 255).astype(int).tolist()
    new_rgb = np.clip(np.rint(new_pixel), 0, 255).astype(int).tolist()

    if operation == "brightness":
        formula = "New channel = clip(Old channel + c, 0, 255)"
        calculation = (
            f"R: {old_rgb[0]} + ({amount}) = {new_rgb[0]}\n"
            f"G: {old_rgb[1]} + ({amount}) = {new_rgb[1]}\n"
            f"B: {old_rgb[2]} + ({amount}) = {new_rgb[2]}"
        )
        explanation = f"The brightness value c = {amount} is added to each RGB channel. Any result below 0 becomes 0, and any result above 255 becomes 255."
    elif operation == "grayscale":
        gray = 0.299 * old_rgb[0] + 0.587 * old_rgb[1] + 0.114 * old_rgb[2]
        formula = "Y = 0.299R + 0.587G + 0.114B"
        calculation = (
            f"Y = 0.299({old_rgb[0]}) + 0.587({old_rgb[1]}) + 0.114({old_rgb[2]})\n"
            f"Y = {gray:.2f} ≈ {new_rgb[0]}\n"
            f"New pixel = ({new_rgb[0]}, {new_rgb[1]}, {new_rgb[2]})"
        )
        explanation = "The RGB channels are combined into one weighted intensity. That same intensity is copied into R, G and B, removing the pixel's colour."
    elif operation == "invert":
        formula = "New channel = 255 − Old channel"
        calculation = (
            f"R: 255 − {old_rgb[0]} = {new_rgb[0]}\n"
            f"G: 255 − {old_rgb[1]} = {new_rgb[1]}\n"
            f"B: 255 − {old_rgb[2]} = {new_rgb[2]}"
        )
        explanation = "Each channel is replaced by its distance from 255. Dark values become light and light values become dark."
    elif operation == "rotate":
        if direction == "counterclockwise":
            formula = "(x, y) → (y, W − 1 − x)"
            calculation = (
                f"Image width W = {width} pixels\n"
                f"Choose pixel at ({x}, {y}).\n"
                f"x′ = y = {y}\n"
                f"y′ = W − 1 − x = {width - 1} − {x} = {width - 1 - x}\n"
                f"New pixel position = ({y}, {width - 1 - x})"
            )
            explanation = "For a 90° counterclockwise rotation, the pixel moves to the old row as its new column, and its column is reversed to become the new row. Pixel colours stay the same."
        else:
            formula = "(x, y) → (H − 1 − y, x)"
            calculation = (
                f"Image height H = {height} pixels\n"
                f"Choose pixel at ({x}, {y}).\n"
                f"x′ = H − 1 − y = {height - 1} − {y} = {height - 1 - y}\n"
                f"y′ = x = {x}\n"
                f"New pixel position = ({height - 1 - y}, {x})"
            )
            explanation = "For a 90° clockwise rotation, the pixel's row determines its new column (reversed), and its old column becomes its new row. Pixel colours stay the same."
    elif operation == "flip_horizontal":
        formula = "(x, y) → (W − 1 − x, y)"
        calculation = (
            f"Image width W = {width} pixels\n"
            f"Choose sample pixel at (x, y) = ({x}, {y}).\n"
            f"x′ = W − 1 − x = {width - 1} − {x} = {width - 1 - x}\n"
            f"y′ = y = {y}\n"
            f"New pixel position = ({width - 1 - x}, {y})"
        )
        explanation = "A horizontal flip reverses the column position. The pixel moves to its mirrored position across the image's vertical centre line; its colour does not change."
    else:
        formula = "(x, y) → (x, H − 1 − y)"
        calculation = (
            f"Image height H = {height} pixels\n"
            f"Choose sample pixel at (x, y) = ({x}, {y}).\n"
            f"x′ = x = {x}\n"
            f"y′ = H − 1 − y = {height - 1} − {y} = {height - 1 - y}\n"
            f"New pixel position = ({x}, {height - 1 - y})"
        )
        explanation = "A vertical flip reverses the row position. The pixel moves to its mirrored position across the image's horizontal centre line; its colour does not change."

    return {
        "name": OPERATIONS[operation],
        "operation": operation,
        "formula": formula,
        "calculation": calculation,
        "explanation": explanation,
        "rotation_direction": direction,
        "old_pixel": old_rgb,
        "new_pixel": new_rgb,
        "old_pixel_text": rgb_text(old_pixel),
        "new_pixel_text": rgb_text(new_pixel),
        "position_transform": operation in {"rotate", "flip_horizontal", "flip_vertical"},
        "old_position": f"({x}, {y})",
        "new_position": f"({mapped_x}, {mapped_y})",
        "new_x": int(mapped_x),
        "new_y": int(mapped_y),
        "before_size": f"{before_size[0]} × {before_size[1]}",
        "after_size": f"{after_size[0]} × {after_size[1]}",
    }


@app.route("/")
def home():
    sample_files = []
    if SAMPLES_FOLDER.exists():
        sample_files = sorted(
            path.name for path in SAMPLES_FOLDER.iterdir()
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
    operations = request.form.getlist("operations")

    if uploaded_file is None:
        return jsonify({"error": "No image was received. Choose an image again."}), 400
    if not operations or any(operation not in OPERATIONS for operation in operations):
        return jsonify({"error": "Choose at least one valid operation."}), 400

    try:
        image = Image.open(uploaded_file.stream).convert("RGB")
        pixels = np.array(image, dtype=np.float32)
        amount = int(request.form.get("amount", "30"))
        direction = request.form.get("rotation_direction", "clockwise")
    except Exception as error:
        return jsonify({"error": f"Could not open the image: {error}"}), 400

    steps = []
    sample_position = (pixels.shape[1] // 2, pixels.shape[0] // 2)
    try:
        for operation in operations:
            before = pixels.copy()
            before_size = (before.shape[1], before.shape[0])

            if operation == "brightness":
                pixels = np.clip(pixels + amount, 0, 255)
            elif operation == "grayscale":
                gray = 0.299 * pixels[:, :, 0] + 0.587 * pixels[:, :, 1] + 0.114 * pixels[:, :, 2]
                pixels = np.stack((gray, gray, gray), axis=2)
            elif operation == "invert":
                pixels = 255 - pixels
            elif operation == "rotate":
                pixels = rotate_90(pixels, direction)
            elif operation == "flip_horizontal":
                pixels = np.flip(pixels, axis=1)
            elif operation == "flip_vertical":
                pixels = np.flip(pixels, axis=0)

            after_size = (pixels.shape[1], pixels.shape[0])
            step = build_step(operation, before, pixels, amount, before_size, after_size, sample_position, direction)
            steps.append(step)
            sample_position = (step["new_x"], step["new_y"])
    except Exception as error:
        return jsonify({"error": f"Could not process the image: {error}"}), 400

    result_image = Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8))
    output = BytesIO()
    result_image.save(output, format="PNG")
    encoded_image = base64.b64encode(output.getvalue()).decode("utf-8")

    return jsonify({
        "image": f"data:image/png;base64,{encoded_image}",
        "steps": steps,
        "operations": operations,
        "width": result_image.width,
        "height": result_image.height,
    })


if __name__ == "__main__":
    app.run(debug=True)
