import cv2
import numpy as np
from PIL import Image
import io
import base64
from utils.config import IMG_SIZE


class ImageProcessor:
    @staticmethod
    def load_image(uploaded_file):
        image_bytes = uploaded_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        return np.array(image)

    @staticmethod
    def load_image_from_bytes(image_bytes):
        image = Image.open(io.BytesIO(image_bytes))
        return np.array(image)

    @staticmethod
    def preprocess_image(image_np):
        if image_np.shape[-1] == 4:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
        elif len(image_np.shape) == 2:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGB)
        resized = cv2.resize(image_np, (IMG_SIZE, IMG_SIZE))
        normalized = resized.astype(np.float32) / 255.0
        return normalized

    @staticmethod
    def prepare_for_model(image_np):
        processed = ImageProcessor.preprocess_image(image_np)
        return np.expand_dims(processed, axis=0)

    @staticmethod
    def generate_heatmap(image_np, prediction_mask=None):
        if len(image_np.shape) == 3 and image_np.shape[-1] == 4:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
        elif len(image_np.shape) == 2:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGB)
        resized = cv2.resize(image_np, (IMG_SIZE, IMG_SIZE))

        if prediction_mask is None:
            gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.threshold(blurred, 0, 255,
                                   cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        else:
            thresh = prediction_mask

        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        heatmap = cv2.applyColorMap(thresh, cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

        overlay = cv2.addWeighted(resized, 0.6, heatmap, 0.4, 0)

        return overlay, heatmap, thresh

    @staticmethod
    def analyze_infection_area(image_np):
        if len(image_np.shape) == 3 and image_np.shape[-1] == 4:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
        elif len(image_np.shape) == 2:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGB)
        resized = cv2.resize(image_np, (IMG_SIZE, IMG_SIZE))

        hsv = cv2.cvtColor(resized, cv2.COLOR_RGB2HSV)

        lower_yellow = np.array([20, 50, 50])
        upper_yellow = np.array([40, 255, 255])
        lower_brown = np.array([10, 50, 50])
        upper_brown = np.array([20, 255, 200])
        lower_dark = np.array([0, 0, 0])
        upper_dark = np.array([180, 255, 80])

        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)
        mask_dark = cv2.inRange(hsv, lower_dark, upper_dark)

        combined_mask = cv2.bitwise_or(mask_yellow, mask_brown)
        combined_mask = cv2.bitwise_or(combined_mask, mask_dark)

        kernel = np.ones((3, 3), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

        infection_pixels = np.count_nonzero(combined_mask)
        total_pixels = IMG_SIZE * IMG_SIZE
        infection_percentage = (infection_pixels / total_pixels) * 100

        infection_percentage = min(infection_percentage, 100.0)

        return infection_percentage, combined_mask

    @staticmethod
    def detect_edges(image_np):
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_np
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        return edges

    @staticmethod
    def get_image_base64(image_np):
        if image_np.dtype != np.uint8:
            image_np = (image_np * 255).astype(np.uint8)
        if len(image_np.shape) == 3 and image_np.shape[-1] == 3:
            pil_img = Image.fromarray(image_np)
        else:
            pil_img = Image.fromarray(image_np)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str

    @staticmethod
    def resize_for_display(image_np, max_width=800):
        h, w = image_np.shape[:2]
        if w > max_width:
            ratio = max_width / w
            new_w = max_width
            new_h = int(h * ratio)
            return cv2.resize(image_np, (new_w, new_h))
        return image_np

    @staticmethod
    def validate_image(uploaded_file):
        if uploaded_file is None:
            return False, "No file provided"
        allowed_types = ["image/jpeg", "image/png", "image/jpg",
                         "image/webp", "image/tiff"]
        if uploaded_file.type not in allowed_types:
            return False, f"Invalid file type: {uploaded_file.type}. Allowed: {', '.join(allowed_types)}"
        max_size = 10 * 1024 * 1024
        if len(uploaded_file.getvalue()) > max_size:
            return False, f"File too large. Maximum size: 10MB"
        return True, "Valid image"

    @staticmethod
    def verify_preprocessing(image_array):
        issues = []
        if image_array.size == 0:
            issues.append("Empty image array")
        if len(image_array.shape) not in (2, 3, 4):
            issues.append(f"Unexpected dimensions: {image_array.shape}")
        if image_array.shape[-1] not in (1, 3, 4):
            issues.append(f"Unexpected channels: {image_array.shape[-1]}")
        mean_val = float(np.mean(image_array))
        if mean_val < 0.01:
            issues.append("Image is near-black (mean pixel < 0.01)")
        elif mean_val > 0.99:
            issues.append("Image is near-white (mean pixel > 0.99)")
        variance = float(np.var(image_array))
        if variance < 0.001:
            issues.append("Image has near-zero variance (possibly blank)")
        return issues
