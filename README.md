# PorygonLab
An app to showcase how the math behind different image filters and editing options works. Pick a picture, try a transformation, and open Math View to see the formula and a small before-and-after matrix sample.

## What you can do

- Upload an image by browsing or dragging it onto the page / choose an image from the `samples` folder
- Adjust brightness
- Convert to grayscale
- Invert colors
- Apply a sepia filter
- Rotate or flip the image
- Open **Math View** to see the operation’s formula and matrix explanation
- Compare a small 4 × 4 pixel-matrix sample before and after the operation

The matrix preview is a small sample to keep the numbers readable. It shows the input red-channel values and the corresponding output values; for grayscale, the output values are grayscale intensities.

## Getting started

### 1. Install Python

Porygon Lab uses Python to run the image-processing app.

### 2. Open the project folder

Open the folder containing `app.py` in VS Code. In VS Code, choose **Terminal → New Terminal**.

### 3. Install the required packages

In the terminal, run:

```powershell
py -m pip install flask pillow numpy
```

### 4. Start the app

Run:

```powershell
py app.py
```

Flask will show a local address in the terminal. Open this one in your browser:

```text
http://127.0.0.1:5000
```

## Sample images

Put JPG, PNG, or WEBP images directly inside the `samples` folder. Restart or refresh the app to see them in the sample list.

```text
Porygon Lab/
├── app.py
├── image_math.py
├── samples/
├── static/
│   └── style.css
└── templates/
    └── index.html
```

## A quick note

This is a learning project, so the math explanations are intentionally visible. For example, brightness adds a constant to pixel values, while sepia uses a color transformation matrix.
