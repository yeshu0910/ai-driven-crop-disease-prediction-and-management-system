import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.image_processor import ImageProcessor


def test_preprocess_image_rgb():
    proc = ImageProcessor()
    img = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    result = proc.preprocess_image(img)
    assert result.shape == (224, 224, 3)
    assert result.dtype == np.float32
    assert 0.0 <= result.min() <= result.max() <= 1.0


def test_preprocess_image_grayscale():
    proc = ImageProcessor()
    img = np.random.randint(0, 256, (224, 224), dtype=np.uint8)
    result = proc.preprocess_image(img)
    assert result.shape == (224, 224, 3)
    assert result.dtype == np.float32


def test_preprocess_image_rgba():
    proc = ImageProcessor()
    img = np.random.randint(0, 256, (224, 224, 4), dtype=np.uint8)
    result = proc.preprocess_image(img)
    assert result.shape == (224, 224, 3)


def test_prepare_for_model():
    proc = ImageProcessor()
    img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    result = proc.prepare_for_model(img)
    assert result.shape == (1, 224, 224, 3)


def test_analyze_infection_area():
    proc = ImageProcessor()
    img = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    pct, mask = proc.analyze_infection_area(img)
    assert 0 <= pct <= 100
    assert mask.shape == (224, 224)
    assert mask.dtype == np.uint8


def test_validate_image_invalid_type():
    proc = ImageProcessor()
    class FakeFile:
        type = "text/plain"
        def getvalue(self):
            return b"test"
    valid, msg = proc.validate_image(FakeFile())
    assert not valid
    assert "Invalid" in msg


def test_validate_image_none():
    proc = ImageProcessor()
    valid, msg = proc.validate_image(None)
    assert not valid
    assert "No file" in msg


def test_resize_for_display():
    proc = ImageProcessor()
    img = np.random.randint(0, 256, (2000, 2000, 3), dtype=np.uint8)
    result = proc.resize_for_display(img, max_width=800)
    assert result.shape[1] == 800


def test_detect_edges():
    proc = ImageProcessor()
    img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    edges = proc.detect_edges(img)
    assert edges.shape == (100, 100)
    assert edges.dtype == np.uint8


def test_generate_heatmap():
    proc = ImageProcessor()
    img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    overlay, heatmap, thresh = proc.generate_heatmap(img)
    assert overlay.shape == (224, 224, 3)
    assert heatmap.shape == (224, 224, 3)
    assert thresh.shape == (224, 224)


def test_get_image_base64():
    proc = ImageProcessor()
    img = np.random.randint(0, 128, (50, 50, 3), dtype=np.uint8)
    b64 = proc.get_image_base64(img)
    assert isinstance(b64, str)
    assert len(b64) > 0


def test_verify_preprocessing_empty():
    proc = ImageProcessor()
    img = np.array([])
    issues = proc.verify_preprocessing(img)
    assert "Empty" in issues[0]


def test_verify_preprocessing_valid():
    proc = ImageProcessor()
    img = np.random.rand(224, 224, 3).astype(np.float32)
    issues = proc.verify_preprocessing(img)
    assert len(issues) == 0


if __name__ == "__main__":
    test_preprocess_image_rgb()
    test_preprocess_image_grayscale()
    test_preprocess_image_rgba()
    test_prepare_for_model()
    test_analyze_infection_area()
    test_validate_image_invalid_type()
    test_validate_image_none()
    test_resize_for_display()
    test_detect_edges()
    test_generate_heatmap()
    test_get_image_base64()
    test_verify_preprocessing_empty()
    test_verify_preprocessing_valid()
    print("All image_processor tests passed!")
