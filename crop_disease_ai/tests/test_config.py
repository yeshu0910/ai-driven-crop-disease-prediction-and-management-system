import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.config import (
    SUPPORTED_CROPS, DISEASE_CLASSES, SEVERITY_LEVELS,
    IMG_SIZE, CONFIDENCE_THRESHOLD, OPENWEATHER_API_KEY,
    BASE_DIR, ASSETS_DIR, DATABASE_DIR, MODELS_DIR, REPORTS_DIR
)


def test_supported_crops_count():
    assert len(SUPPORTED_CROPS) == 15


def test_supported_crops_content():
    expected = {"Tomato", "Potato", "Rice", "Wheat", "Corn", "Cotton",
                "Soybean", "Sugarcane", "Groundnut", "Sunflower", "Banana",
                "Mango", "Grapes", "Apple", "Chili"}
    assert set(SUPPORTED_CROPS) == expected


def test_disease_classes_count():
    assert len(DISEASE_CLASSES) == 57


def test_disease_classes_structure():
    for key, value in DISEASE_CLASSES.items():
        assert "___" in key or "_" in key
        assert value


def test_disease_classes_have_all_crops():
    crop_set = set(SUPPORTED_CROPS)
    for key in DISEASE_CLASSES:
        crop = key.split("___")[0]
        # Handle multi-word crop names
        crop_words = crop.split("_")
        # Map to our format
        assert crop_set.intersection({crop_words[0]})


def test_severity_levels():
    assert "Healthy" in SEVERITY_LEVELS
    assert "Mild" in SEVERITY_LEVELS
    assert "Moderate" in SEVERITY_LEVELS
    assert "Severe" in SEVERITY_LEVELS


def test_severity_level_properties():
    for level, props in SEVERITY_LEVELS.items():
        assert "color" in props
        assert "icon" in props
        assert "risk" in props


def test_img_size():
    assert IMG_SIZE == 224


def test_confidence_threshold():
    assert 0 < CONFIDENCE_THRESHOLD <= 1.0


def test_dirs_exist():
    assert BASE_DIR.exists()
    assert ASSETS_DIR.exists()
    assert DATABASE_DIR.exists()
    assert MODELS_DIR.exists()
    assert REPORTS_DIR.exists()


def test_each_crop_has_healthy_entry():
    for crop in SUPPORTED_CROPS:
        healthy_key = f"{crop}___healthy"
        assert healthy_key in DISEASE_CLASSES, f"Missing healthy entry for {crop}"


if __name__ == "__main__":
    test_supported_crops_count()
    test_supported_crops_content()
    test_disease_classes_count()
    test_disease_classes_structure()
    test_disease_classes_have_all_crops()
    test_severity_levels()
    test_severity_level_properties()
    test_img_size()
    test_confidence_threshold()
    test_dirs_exist()
    test_each_crop_has_healthy_entry()
    print("All config tests passed!")
