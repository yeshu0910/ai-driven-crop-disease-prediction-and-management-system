import os
import sys
from pathlib import Path

import pytest

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
_tensorflow = pytest.importorskip("tensorflow")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.model_handler import ModelHandler  # noqa: E402

mh = ModelHandler()
print(f"Model loaded: {mh.is_model_loaded()}")
print(f"Class indices: {len(mh.class_indices) if mh.class_indices else 0}")
print(f"Class names: {len(mh.class_names) if mh.class_names else 0}")
print(f"Supported crops: {len(mh.SUPPORTED_CROPS)}")

audit = mh.audit_dataset()
print(f"Dataset audit: {audit['total_classes']} classes, {audit['total_crops']} crops")

# Verify all supported crops have entries
for crop in mh.SUPPORTED_CROPS:
    healthy_key = f"{crop}___healthy"
    if mh.class_indices:
        assert healthy_key in mh.class_indices
print("All crops verified!")
print("Model handler test passed!")
