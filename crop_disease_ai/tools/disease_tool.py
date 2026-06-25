# Disease prediction wrapper tool for ADK
from typing import Any, Dict, Optional

import numpy as np


# ADK typed function
def predict_disease_tool(
    image_array: np.ndarray, crop_hint: Optional[str] = None
) -> Dict[str, Any]:
    from utils.model_handler import ModelHandler

    model = ModelHandler()
    return model.predict(image_array, crop_hint=crop_hint)
