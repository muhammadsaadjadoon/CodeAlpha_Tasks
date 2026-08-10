from dataclasses import dataclass
from io import BytesIO
import base64
import cv2
import numpy as np
from PIL import Image, ImageOps

@dataclass
class ProcessedCharacter:
    tensor: np.ndarray
    preview_data_url: str
    foreground_ratio: float

def _shift_to_center(image: np.ndarray) -> np.ndarray:
    moments = cv2.moments(image)
    if abs(moments["m00"]) < 1e-6: return image
    cx, cy = moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]
    shift_x, shift_y = int(round(13.5 - cx)), int(round(13.5 - cy))
    matrix = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    return cv2.warpAffine(image, matrix, (28, 28), flags=cv2.INTER_LINEAR, borderValue=0)

def preprocess_character(raw: bytes) -> ProcessedCharacter:
    try:
        source = Image.open(BytesIO(raw))
        source = ImageOps.exif_transpose(source).convert("RGBA")
    except Exception as exc:
        raise ValueError("The uploaded file is not a valid image.") from exc
    if max(source.size) > 2400:
        source.thumbnail((2400, 2400), Image.Resampling.LANCZOS)
    white = Image.new("RGBA", source.size, (255,255,255,255))
    white.alpha_composite(source)
    gray = np.array(white.convert("L"), dtype=np.uint8)
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    # MNIST/EMNIST convention: bright foreground on dark background.
    if float(gray.mean()) > 127:
        gray = 255 - gray
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    coords = cv2.findNonZero(mask)
    if coords is None:
        raise ValueError("No visible character was detected.")
    x, y, w, h = cv2.boundingRect(coords)
    if w < 2 or h < 2:
        raise ValueError("The detected mark is too small.")
    crop = gray[y:y+h, x:x+w]
    side = max(w, h)
    pad = max(4, int(round(side * 0.18)))
    canvas_side = side + 2 * pad
    canvas = np.zeros((canvas_side, canvas_side), dtype=np.uint8)
    oy = (canvas_side - h)//2; ox = (canvas_side - w)//2
    canvas[oy:oy+h, ox:ox+w] = crop
    scaled_side = 20
    ratio = min(scaled_side / canvas.shape[1], scaled_side / canvas.shape[0])
    nw = max(1, int(round(canvas.shape[1]*ratio))); nh = max(1, int(round(canvas.shape[0]*ratio)))
    resized = cv2.resize(canvas, (nw, nh), interpolation=cv2.INTER_AREA)
    out = np.zeros((28,28), dtype=np.uint8)
    ox=(28-nw)//2; oy=(28-nh)//2
    out[oy:oy+nh, ox:ox+nw] = resized
    out = _shift_to_center(out)
    foreground_ratio = float((out > 32).mean())
    normalized = ((out.astype(np.float32)/255.0)-0.5)/0.5
    preview = Image.fromarray(out, mode="L")
    buf=BytesIO(); preview.save(buf, format="PNG")
    data_url="data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode()
    return ProcessedCharacter(normalized[None,None,:,:], data_url, foreground_ratio)
