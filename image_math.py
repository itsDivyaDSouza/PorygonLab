from PIL import Image
import numpy as np

def load_path(path):
    image=Image.open(path).convert("RGB")
    pixels = np.array(image, dtype=np.float32)
    return pixels

def save_image(pixels, path):
    pixels = np.clip(pixels,0,255).astype(np.uint8)
    image = Image.fromarray(pixels)
    image.save(path)

def brightness(pixels, amt):
    bright = pixels + amt
    return np.clip(bright, 0,255)

def grayscale(pixels):
    red = pixels [:,:,0]
    green = pixels [:,:,1]
    blue = pixels [:,:,2]

    gray = 0.299 * red + 0.587 * green + 0.114 * blue
    grayscale = np.stack((gray,gray,gray), axis=2)
    return grayscale


def invert(pixels):
    return 255-pixels

def sepia(pixels):
    sepia_matrix = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])

    sepia = pixels @ sepia_matrix.T
    return np.clip(sepia, 0, 255)

def rotate(pixels, degrees):
    if degrees not in (90, 180, 270):
        raise ValueError(" it shud be in 90, 180 or 270 degrees")

    return np.rot90(pixels, k=degrees // 90, axes=(0,1))

def flip(pixels, direction):

    if direction == "horizontal":
        return np.flip(pixels, axis=1)
    elif direction == "vertical":
        return np.flip(pixels, axis=0)
    else:
        raise ValueError("direction must be horizontal or vertical")

if __name__ == "__main__":
    from pathlib import Path

    samples_folder = Path("samples")
    sample_images =  list(samples_folder.glob("*"))

for index, image_path in enumerate(sample_images, start=1):
        print(f"{index}. {image_path.name}")

        choice = int(input("Choose an image number: "))
        selected_path = sample_images[choice - 1]

        original = load_path(selected_path)

        print("\nChoose an operation:")
        print("1. Brightness")
        print("2. Grayscale")
        print("3. Invert")
        print("4. Sepia")
        print("5. Rotate")
        print("6. Flip")

        operation = input("Enter an operation number: ")

        if operation == "1":
            amount = int(input("Brightness amount (-255 to 255): "))
            result = brightness(original, amount)
        elif operation == "2":
            result = grayscale(original)
        elif operation == "3":
            result = invert(original)
        elif operation == "4":
            result = sepia(original)
        elif operation == "5":
            degrees = int(input("Rotate by 90, 180, or 270 degrees: "))
            result = rotate(original, degrees)
        elif operation == "6":
            direction = input("Flip horizontally or vertically? ").lower()
            result = flip(original, direction)
        else:
            print("Invalid operation number mate")
            raise SystemExit

        output_folder = Path("outputs")
        output_folder.mkdir(exist_ok=True)

        output_path = output_folder / f"edited_{selected_path.name}"
        save_image(result, output_path)

        print(f"Edited image saved to: {output_path}")    


