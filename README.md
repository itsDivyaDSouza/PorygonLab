# PorygonLab

An app to showcase how the math behind different image filters and editing options works. Pick a picture, try a transformation, and open Math View to see the formula and a before-and-after pixel sample.

## What you can do

- Upload an image by browsing or dragging it onto the page
- Choose a sample image from the `samples` folder
- Adjust brightness
- Convert an image to grayscale
- Invert the colours
- Rotate the image by 90°
- Flip the image horizontally or vertically
- Open **Math View** to see each operation’s formula and explanation
- Compare sample pixel values before and after an operation

## Getting started

### 1. Install Python

PorygonLab uses Python to run the image-processing app.

### 2. Open the project folder

Open the folder containing `app.py` in VS Code. Then choose **Terminal → New Terminal**.

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

Flask will show a local address in the terminal. Open this address in your browser:

```text
http://127.0.0.1:5000
```

## Sample images

Put JPG, JPEG, PNG, or WEBP images directly inside the `samples` folder. Refresh the page to see them in the sample list.

```text
Porygon Lab/
├── app.py
├── samples/
├── static/
│   └── style.css
└── templates/
    └── index.html
```

Have fun messing around with the filters :P