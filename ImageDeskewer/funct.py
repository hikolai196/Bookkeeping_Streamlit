import numpy as np
import cv2
from PIL import Image
import io
import math

def load_image(file):
    """
    Load an image file and convert it to RGB format and a NumPy array.

    Args:
        file: A file-like object containing the image.
    Returns:
        tuple: A tuple (image, img_np) where 'image' is a PIL Image in RGB mode,
               and 'img_np' is the corresponding NumPy array.
    Raises:
        Exception: If the file cannot be opened or is not a valid image.
    """
    image = Image.open(file).convert("RGB")
    img_np = np.array(image)
    return image, img_np

def resize_image(img_np, max_dim=600):
    """
    Resize an image to fit within a square of size max_dim, preserving aspect ratio.

    Args:
        img_np (np.ndarray): The input image as a NumPy array.
        max_dim (int, optional): The maximum width or height of the resized image. Default is 600.
    Returns:
        tuple: A tuple (resized_img, scale) where 'resized_img' is the resized image as a NumPy array,
               and 'scale' is the scaling factor applied.
    """
    h, w = img_np.shape[:2]
    # Only scale down if image is larger than max_dim
    if max(h, w) > max_dim:
        scale = min(max_dim / w, max_dim / h)
    else:
        scale = 1.0  # No scaling (no upscaling)
    display_w, display_h = max(1, int(w * scale)), max(1, int(h * scale))
    resized_img = cv2.resize(img_np, (display_w, display_h), interpolation=cv2.INTER_AREA)
    return resized_img, scale

def are_points_valid(points, min_distance=5):
    """
    Validate that four points are suitable for a perspective transform.

    Args:
        points (list): List of four [x, y] points.
        min_distance (float, optional): Minimum allowed distance between any two points.
    Returns:
        tuple: (is_valid, message) where is_valid is a boolean and message is a string explanation.
    """
    if len(points) != 4:
        return False, "Exactly 4 points are required."
    pts = np.array(points, dtype="float32")
    if len(set(tuple(map(int, pt)) for pt in pts)) != 4:
        return False, "Points must be unique."
    for i in range(4):
        for j in range(i+1, 4):
            if np.linalg.norm(pts[i] - pts[j]) < min_distance:
                return False, "Points are too close together."
    def area_quad(pts):
        return 0.5 * abs(
            pts[0][0]*pts[1][1] + pts[1][0]*pts[2][1] +
            pts[2][0]*pts[3][1] + pts[3][0]*pts[0][1] -
            (pts[1][0]*pts[0][1] + pts[2][0]*pts[1][1] +
             pts[3][0]*pts[2][1] + pts[0][0]*pts[3][1])
        )
    if area_quad(pts) < 1.0:
        return False, "Selected points are nearly collinear or form a degenerate quadrilateral."
    return True, ""

def deskew_image(img_np, points):
    """
    Apply a perspective transform to deskew an image based on four corner points.

    Args:
        img_np (np.ndarray): The original image as a NumPy array.
        points (list): List of four [x, y] corner points in the order:
                       top-left, top-right, bottom-right, bottom-left.
    Returns:
        PIL.Image.Image: The deskewed image as a PIL Image.
    Raises:
        ValueError: If the points are invalid for perspective transformation.
    """
    valid, msg = are_points_valid(points)
    if not valid:
        raise ValueError(f"Invalid points for deskewing: {msg}")
    pts_src = np.array(points, dtype="float32")
    wA = np.linalg.norm(pts_src[0] - pts_src[1])
    wB = np.linalg.norm(pts_src[2] - pts_src[3])
    maxW = math.ceil(max(wA, wB))
    hA = np.linalg.norm(pts_src[0] - pts_src[3])
    hB = np.linalg.norm(pts_src[1] - pts_src[2])
    maxH = math.ceil(max(hA, hB))
    pts_dst = np.array([
        [0, 0],
        [maxW - 1, 0],
        [maxW - 1, maxH - 1],
        [0, maxH - 1]
    ], dtype="float32")
    M = cv2.getPerspectiveTransform(pts_src, pts_dst)
    warped = cv2.warpPerspective(img_np, M, (maxW, maxH))
    return Image.fromarray(warped)

def label_corners(points, scale):
    """
    Convert points from display coordinates to original image coordinates.

    Args:
        points (list): List of [x, y] points from the resized image.
        scale (float): The scaling factor used during resizing.
    Returns:
        list: List of [x, y] points mapped to the original image size.
    """
    return [[int(x / scale), int(y / scale)] for x, y in points]

def image_to_bytes(img, fmt):
    """
    Convert a PIL Image to bytes in the specified format.

    Args:
        img (PIL.Image.Image): The image to convert.
        fmt (str): The format to use ('PNG' or 'JPG').
    Returns:
        bytes: The image data in the specified format.
    """
    buf = io.BytesIO()
    ext = "PNG" if fmt.upper() == "PNG" else "JPEG"
    img.save(buf, format=ext)
    return buf.getvalue()