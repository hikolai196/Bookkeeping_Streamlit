# Image Deskewer
A simple, interactive web app for deskewing images by selecting four corner points. Built with Streamlit, this tool allows you to upload a photo, mark the corners of a document or region, and download a perspective-corrected (deskewed) version.
---
## Features
- Easy Upload: Supports PNG and JPG images.
- Interactive Corner Selection: Click and drag to select and adjust four corners.
- Automatic Resizing: Large images are resized for easier annotation.
- Deskewing: Applies a perspective transform to correct skewed images.
- Download Output: Save the deskewed image as PNG or JPG.
- Mobile Friendly: Works on desktop and mobile devices.
## Demo
Failed to load image.

Select four corners and download your deskewed image!

## Installation
    1. Clone the repository:
BASH
```
git clone https://github.com/yourusername/image-deskewer.git
    cd image-deskewer
```
    2. Install dependencies:
BASH
```
pip install -r requirements.txt
```
*Required packages: `streamlit`, `streamlit-drawable-canvas`, `opencv-python`, `numpy`, `Pillow`*
---
## Usage
    1. Run the app:
BASH
```
streamlit run main.py
```
    2. How to use:
        - Upload a PNG or JPG image.
        - Click on the image to select four points (in order: top-left, top-right, bottom-right, - bottom-left).
        - Adjust points as needed.
        - Choose output format (PNG or JPG).
        - Download the deskewed result.
---
## File Structure
```
.
├── funct.py      # Core image processing functions (load, resize, deskew, etc.)
├── sui.py        # Streamlit UI and interaction logic
├── main.py       # App entry point
├── requirements.txt
└── README.md
```
## Module Overview
- funct.py:
    - Image loading, resizing, validation, perspective transform, and output conversion.
- sui.py:
    - Streamlit UI, canvas for point selection, and integration with processing functions.
- main.py:
    - Launches the app.
---
## Tips
- Select points in the order: top-left → top-right → bottom-right → bottom-left.
- Use the eraser or reload the image to reset points.
- For best results on mobile, use a stylus or your finger.
---
## Troubleshooting
- Error loading image: Ensure the file is a valid PNG or JPG.
- Deskewing fails: Make sure points are not too close and form a proper quadrilateral.
- App not starting: Check that all dependencies are installed.
## License
MIT License