import logging
import sys
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf

# Add parent directory to path for Streamlit Cloud compatibility
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.config import (
    CLASS_INDICES_PATH,
    CONFIDENCE_THRESHOLD,
    CROP_CONFIDENCE_THRESHOLD,
    DISEASE_CLASSES,
    IMG_SIZE,
    MODEL_PATH,
    SUPPORTED_CROPS,
)

logger = logging.getLogger(__name__)


class ModelHandler:
    SUPPORTED_CROPS = SUPPORTED_CROPS

    def __init__(self):
        self.model = None
        self.class_indices = None
        self.class_names = None
        self.load_model()

    def load_model(self):
        if MODEL_PATH.exists():
            try:
                self.model = tf.keras.models.load_model(str(MODEL_PATH))
                logger.info(f"Model loaded from {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self.model = None
        else:
            logger.warning(f"Model not found at {MODEL_PATH}")
            self.model = None

        if CLASS_INDICES_PATH.exists():
            try:
                self.class_indices = np.load(
                    str(CLASS_INDICES_PATH), allow_pickle=True
                ).item()
                self.class_names = {v: k for k, v in self.class_indices.items()}
                logger.info(f"Class indices loaded: {len(self.class_indices)} classes")
            except Exception as e:
                logger.error(f"Failed to load class indices: {e}")
                self.class_indices = None
                self.class_names = None
        else:
            logger.warning(f"Class indices not found at {CLASS_INDICES_PATH}")
            self.class_indices = None
            self.class_names = None

    def _validate_model_prediction(self, probs, predicted_idx, class_name):
        errors = []
        if predicted_idx not in self.class_names:
            errors.append(f"Index {predicted_idx} not in class_names map")
        if class_name and class_name not in DISEASE_CLASSES:
            errors.append(f"Class '{class_name}' not in DISEASE_CLASSES config")
        if self.class_indices and class_name:
            expected_idx = self.class_indices.get(class_name)
            if expected_idx is not None and expected_idx != predicted_idx:
                errors.append(
                    f"Index mismatch: predicted {predicted_idx}, but {class_name} maps to {expected_idx}"
                )
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        max_entropy = np.log(len(probs))
        norm_entropy = entropy / max_entropy
        if norm_entropy > 0.95:
            errors.append(
                f"Near-uniform distribution (norm_entropy={norm_entropy:.3f})"
            )
        sorted_probs = sorted(probs, reverse=True)
        margin = sorted_probs[0] - sorted_probs[1] if len(sorted_probs) > 1 else 0
        if margin < 0.01:
            errors.append(f"Negligible margin over 2nd: {margin:.4f}")
        return errors, norm_entropy, margin

    def predict(self, image_array, crop_hint=None):
        features = self._analyze_image(image_array)
        crop_analysis = self._detect_crop_type(features)
        crop_name_h, crop_confidence_h, top5_crops = crop_analysis
        all_crop_scores = {c: round(s, 1) for c, s in top5_crops}

        disease_unknown_threshold = 0.001
        model_reliable_threshold = 0.001

        effective_crop = crop_name_h
        if crop_hint and crop_hint in SUPPORTED_CROPS:
            effective_crop = crop_hint
            crop_confidence_h = 1.0
        else:
            crop_confidence_h = round(crop_confidence_h, 3)

        model_predictions = None
        model_predicted_idx = None
        model_class_name = None
        model_raw_probs = None

        if self.model is not None:
            try:
                model_raw_probs = self.model.predict(image_array, verbose=0)
                model_predictions = model_raw_probs[0]
                model_predicted_idx = int(np.argmax(model_predictions))
                if self.class_names:
                    model_class_name = self.class_names.get(
                        model_predicted_idx, f"Class_{model_predicted_idx}"
                    )
                else:
                    model_class_name = f"Class_{model_predicted_idx}"
            except Exception as e:
                logger.error(f"Model prediction error: {e}")

        best_disease = None
        best_confidence = 0.0
        top_5_predictions = []
        raw_model_all = []

        if model_predictions is not None and self.class_names:
            all_sorted = np.argsort(model_predictions)[::-1]
            all_indices = [int(i) for i in all_sorted]

            raw_model_all = [
                {
                    "class_name": self.class_names.get(int(i), f"Class_{int(i)}"),
                    "disease_name": DISEASE_CLASSES.get(
                        self.class_names.get(int(i), ""),
                        self.class_names.get(int(i), f"Class_{int(i)}"),
                    ),
                    "confidence": float(model_predictions[int(i)]),
                    "index": int(i),
                }
                for i in all_indices
            ]

            filtered = []
            for idx in all_indices:
                cn = self.class_names.get(idx, "")
                if not cn:
                    continue
                pred_crop = self._extract_crop_from_class(cn)
                if pred_crop and pred_crop == effective_crop:
                    dn = DISEASE_CLASSES.get(cn, cn)
                    conf = float(model_predictions[idx])
                    filtered.append(
                        {
                            "class_name": cn,
                            "disease_name": dn,
                            "confidence": conf,
                            "index": idx,
                        }
                    )

            if filtered:
                best = filtered[0]
                best_disease = best["disease_name"]
                best_confidence = best["confidence"]
                if (
                    raw_model_all
                    and raw_model_all[0]["confidence"] > best_confidence * 1.5
                ):
                    best_disease = raw_model_all[0]["disease_name"]
                    best_confidence = raw_model_all[0]["confidence"]
                    effective_crop = self._extract_crop_from_class(
                        raw_model_all[0]["class_name"]
                    )
            elif raw_model_all and model_predictions is not None:
                top_pred = raw_model_all[0]
                best_disease = top_pred["disease_name"]
                best_confidence = top_pred["confidence"]

            top_5_predictions = raw_model_all[:5]

        model_is_reliable = (
            model_predictions is not None
            and best_confidence >= model_reliable_threshold
            and best_disease is not None
        )

        if not model_is_reliable:
            feature_disease, feature_conf, feature_healthy = (
                self._detect_disease_from_features(features, effective_crop)
            )
            if feature_conf > best_confidence:
                best_disease = feature_disease
                best_confidence = feature_conf
                top_5_predictions = raw_model_all[:5] if raw_model_all else []

        if best_disease is None or best_confidence < disease_unknown_threshold:
            return self._build_unknown_result(
                top5_crops,
                effective_crop,
                model_predictions=model_predictions,
                all_scores=all_crop_scores,
            )

        is_low_confidence = best_confidence < CONFIDENCE_THRESHOLD
        is_healthy = "healthy" in best_disease.lower()

        if not top_5_predictions:
            if raw_model_all:
                top_5_predictions = raw_model_all[:5]
            else:
                top_5_predictions = self._build_disease_list_for_crop(
                    effective_crop, best_disease, features
                )

        raw_top5 = raw_model_all[:5] if raw_model_all else None

        validation_errors, norm_entropy, margin = (
            self._validate_model_prediction(
                model_predictions, model_predicted_idx, model_class_name
            )
            if model_predictions is not None and model_class_name
            else ([], 0.0, 0.0)
        )

        result = {
            "success": True,
            "disease_name": best_disease,
            "crop_name": effective_crop,
            "confidence": min(best_confidence, 0.98),
            "is_healthy": is_healthy,
            "is_low_confidence": is_low_confidence,
            "class_index": 0,
            "top_3_predictions": top_5_predictions[:3],
            "top_5_predictions": top_5_predictions[:5],
            "all_confidences": [],
            "model_used": "trained" if self.model else "image_analysis",
            "crop_confidence": round(crop_confidence_h, 3),
            "top_5_crops": [{"crop": c, "score": round(s, 1)} for c, s in top5_crops],
            "prediction_quality": {
                "norm_entropy": round(norm_entropy, 4) if norm_entropy else 0,
                "margin": round(margin, 4) if margin else 0,
                "validation_errors": validation_errors,
            },
            "raw_model_top5": raw_top5,
        }

        if model_predictions is not None:
            result["all_confidences"] = (
                model_predictions.tolist()
                if hasattr(model_predictions, "tolist")
                else list(model_predictions)
            )
            result["class_index"] = int(model_predicted_idx)

        return result

    def _build_unknown_result(
        self, top5_crops, crop_name=None, all_scores=None, model_predictions=None
    ):
        if crop_name:
            disease_name = f"{crop_name} (Uncertain)"
            crop_display = crop_name
            confidence = 0.0
            model_used = "unknown_disease"
        else:
            disease_name = "Unknown Crop"
            crop_display = "Unknown"
            confidence = 0.0
            model_used = "unknown_crop"

        top5_list = []
        if model_predictions is not None and self.class_names:
            all_sorted = np.argsort(model_predictions)[::-1]
            for i in all_sorted[:5]:
                cn = self.class_names.get(int(i), f"Class_{int(i)}")
                dn = DISEASE_CLASSES.get(cn, cn)
                top5_list.append(
                    {
                        "class_name": cn,
                        "disease_name": dn,
                        "confidence": float(model_predictions[int(i)]),
                        "index": int(i),
                    }
                )

        while len(top5_list) < 5:
            top5_list.append(
                {
                    "class_name": "unknown",
                    "disease_name": disease_name,
                    "confidence": 0.0,
                }
            )

        result = {
            "success": True,
            "disease_name": disease_name,
            "crop_name": crop_display,
            "confidence": confidence,
            "is_healthy": False,
            "is_low_confidence": True,
            "class_index": 0,
            "top_3_predictions": top5_list[:3],
            "top_5_predictions": top5_list[:5],
            "all_confidences": model_predictions.tolist()
            if model_predictions is not None
            else [],
            "model_used": model_used,
            "crop_confidence": 0.0,
            "top_5_crops": [{"crop": c, "score": round(s, 1)} for c, s in top5_crops],
            "raw_model_top5": top5_list[:5] if model_predictions is not None else None,
        }
        if all_scores:
            result["all_crop_scores"] = all_scores
        return result

    def _build_disease_list_for_crop(self, crop_name, primary_disease, features):
        crop_disease_list = [
            v for k, v in DISEASE_CLASSES.items() if v.startswith(crop_name)
        ]
        healthy_name = f"{crop_name} Healthy"
        result = []
        result.append(
            {
                "class_name": f"{crop_name}_primary",
                "disease_name": primary_disease,
                "confidence": 1.0,
            }
        )
        if healthy_name in crop_disease_list and healthy_name != primary_disease:
            result.append(
                {
                    "class_name": f"{crop_name}_healthy",
                    "disease_name": healthy_name,
                    "confidence": max(0.05, (100 - features.get("brown_pct", 0)) / 200),
                }
            )
        for other in crop_disease_list:
            if len(result) >= 5:
                break
            if other != primary_disease and other != healthy_name:
                result.append(
                    {
                        "class_name": f"{crop_name}_other",
                        "disease_name": other,
                        "confidence": 0.3,
                    }
                )
        while len(result) < 5:
            result.append(
                {
                    "class_name": f"{crop_name}_alt",
                    "disease_name": f"{crop_name} (alternative)",
                    "confidence": 0.01,
                }
            )
        return result

    @staticmethod
    def _extract_crop_from_class(class_name):
        if not class_name or class_name.startswith("Class_"):
            return None
        return class_name.split("___")[0].split("_")[0]

    def _is_prediction_reliable(self, probs, top_conf, validation_errors=None):
        if top_conf < CONFIDENCE_THRESHOLD:
            return False
        if validation_errors and len(validation_errors) > 0:
            return False
        sorted_probs = sorted(probs, reverse=True)
        return not (len(sorted_probs) > 1 and sorted_probs[0] - sorted_probs[1] < 0.05)

    def _analyze_image(self, image_array):
        img = (
            image_array[0]
            if image_array.shape[0] == 1 and len(image_array.shape) == 4
            else image_array
        )
        if img.dtype != np.uint8:
            img = (img * 255).astype(np.uint8)
        if img.shape[-1] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        elif len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))

        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        h, s, v = cv2.split(hsv)
        l_ch, a_ch, b_ch = cv2.split(lab)

        green_mask = cv2.inRange(hsv, (35, 30, 30), (85, 255, 255))
        green_pct = np.count_nonzero(green_mask) / (IMG_SIZE * IMG_SIZE) * 100

        yellow_mask = cv2.inRange(hsv, (20, 50, 50), (35, 255, 255))
        yellow_pct = np.count_nonzero(yellow_mask) / (IMG_SIZE * IMG_SIZE) * 100

        brown_mask = cv2.inRange(hsv, (5, 50, 30), (20, 200, 150))
        brown_pct = np.count_nonzero(brown_mask) / (IMG_SIZE * IMG_SIZE) * 100

        dark_mask = cv2.inRange(lab, (0, 0, 0), (80, 130, 130))
        dark_pct = np.count_nonzero(dark_mask) / (IMG_SIZE * IMG_SIZE) * 100

        white_mask = cv2.inRange(hsv, (0, 0, 150), (180, 40, 255))
        white_pct = np.count_nonzero(white_mask) / (IMG_SIZE * IMG_SIZE) * 100

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 100)
        edge_density = np.count_nonzero(edges) / (IMG_SIZE * IMG_SIZE) * 100

        mean_hue = float(np.mean(h))
        mean_sat = float(np.mean(s))
        mean_val = float(np.mean(v))
        mean_green_val = (
            float(np.mean(green_mask)) / 255.0 * 100
            if np.count_nonzero(green_mask) > 0
            else 0
        )

        return {
            "green_pct": green_pct,
            "yellow_pct": yellow_pct,
            "brown_pct": brown_pct,
            "dark_pct": dark_pct,
            "white_pct": white_pct,
            "edge_density": edge_density,
            "mean_green": mean_green_val,
            "mean_hue": mean_hue,
            "mean_saturation": mean_sat,
            "mean_value": mean_val,
            "mean_l": float(np.mean(l_ch)),
            "mean_a": float(np.mean(a_ch)),
            "mean_b": float(np.mean(b_ch)),
        }

    def _detect_crop_type(self, features):
        green_pct = features["green_pct"]
        mean_hue = features["mean_hue"]
        mean_val = features["mean_value"]
        edge_density = features["edge_density"]
        yellow_pct = features["yellow_pct"]
        brown_pct = features["brown_pct"]

        scores = {}
        for crop in SUPPORTED_CROPS:
            scores[crop] = 0.0

        if green_pct > 60:
            for c in ["Rice", "Wheat", "Sugarcane", "Corn"]:
                scores[c] += 18
            scores["Banana"] += 8
            scores["Mango"] += 6
        elif green_pct > 45:
            for c in ["Soybean", "Potato", "Cotton"]:
                scores[c] += 14
            for c in ["Tomato", "Banana"]:
                scores[c] += 10
            scores["Mango"] += 8
            scores["Apple"] += 6
        elif green_pct > 30:
            for c in ["Chili", "Groundnut"]:
                scores[c] += 10
            for c in ["Sunflower", "Mango"]:
                scores[c] += 8
            for c in ["Apple", "Grapes"]:
                scores[c] += 6
        else:
            for c in ["Apple", "Mango", "Banana", "Grapes"]:
                scores[c] += 10

        mean_hue_scaled = mean_hue / 2.0
        scores["Rice"] += max(0, 10 - abs(mean_hue_scaled - 42))
        scores["Wheat"] += max(0, 10 - abs(mean_hue_scaled - 38))
        scores["Corn"] += max(0, 10 - abs(mean_hue_scaled - 40))
        scores["Tomato"] += max(0, 10 - abs(mean_hue_scaled - 45))

        if edge_density > 18:
            for c in ["Corn", "Wheat", "Rice", "Sugarcane"]:
                scores[c] += 6
        elif edge_density > 10:
            for c in ["Soybean", "Potato"]:
                scores[c] += 5
        else:
            for c in ["Banana", "Mango"]:
                scores[c] += 8
            scores["Apple"] += 6

        if mean_val > 160:
            scores["Cotton"] += 8
            scores["Sunflower"] += 7
        elif mean_val < 90:
            scores["Grapes"] += 7
            scores["Sugarcane"] += 5

        if yellow_pct > 8:
            scores["Potato"] += 5
            scores["Tomato"] += 4
        if brown_pct > 8:
            scores["Rice"] += 5
            scores["Wheat"] += 4

        if features["mean_a"] > 5:
            for c in ["Apple", "Mango"]:
                scores[c] += 5
            scores["Tomato"] += 3

        if features["mean_b"] > 15:
            scores["Banana"] += 5
            scores["Mango"] += 4

        white_pct = features.get("white_pct", 0)
        if white_pct > 10:
            for c in ["Mango", "Apple", "Grapes"]:
                scores[c] += 5
            scores["Tomato"] += 4

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_crop = sorted_scores[0][0]
        top_score = sorted_scores[0][1]

        crop_confidence = 0.0
        total = sum(s for _, s in sorted_scores[:5])
        if total > 0:
            crop_confidence = top_score / total if total > 0 else 0

        return top_crop, crop_confidence, sorted_scores[:5]

    def _detect_disease_from_features(self, features, crop_name):
        green_pct = features.get("green_pct", 0)
        yellow_pct = features.get("yellow_pct", 0)
        brown_pct = features.get("brown_pct", 0)
        dark_pct = features.get("dark_pct", 0)
        white_pct = features.get("white_pct", 0)

        yellow_pct * 0.5 + brown_pct * 0.8 + dark_pct * 0.3 + white_pct * 0.4

        crop_disease_list = [
            v for k, v in DISEASE_CLASSES.items() if v.startswith(crop_name)
        ]

        if not crop_disease_list:
            return f"{crop_name} Healthy", 0.9, True

        healthy_name = f"{crop_name} Healthy"
        has_healthy = healthy_name in crop_disease_list
        total_abnormal = yellow_pct + brown_pct + dark_pct + white_pct

        if total_abnormal < 10:
            if has_healthy:
                base_conf = 0.70 + (green_pct / 100) * 0.25
                return healthy_name, min(base_conf, 0.98), True
            return crop_disease_list[0], 0.5, False

        if white_pct > 10:
            keywords = ["mildew", "powdery", "white", "mold"]
            candidates = [
                d
                for d in crop_disease_list
                if d != healthy_name and any(kw in d.lower() for kw in keywords)
            ]
            if candidates:
                conf = min(0.50 + white_pct / 100, 0.92)
                return candidates[0], conf, False

        if brown_pct > 12 or dark_pct > 15:
            keywords = ["blight", "spot", "rust", "rot", "scab", "blast"]
            candidates = [
                d
                for d in crop_disease_list
                if d != healthy_name and any(kw in d.lower() for kw in keywords)
            ]
            if candidates:
                conf = min(0.50 + total_abnormal / 150, 0.92)
                return candidates[0], conf, False

        if yellow_pct > brown_pct and yellow_pct > 12:
            keywords = ["yellow", "mosaic", "curl", "virus", "mildew"]
            candidates = [
                d
                for d in crop_disease_list
                if d != healthy_name and any(kw in d.lower() for kw in keywords)
            ]
            if candidates:
                conf = min(0.50 + yellow_pct / 100, 0.88)
                return candidates[0], conf, False

        non_healthy = [d for d in crop_disease_list if d != healthy_name]
        if non_healthy and total_abnormal > 15:
            conf = min(0.40 + total_abnormal / 200, 0.80)
            return non_healthy[0], conf, False

        if has_healthy and total_abnormal < 20:
            conf = 0.65 + (green_pct / 100) * 0.20
            return healthy_name, min(conf, 0.90), True

        if non_healthy:
            return non_healthy[0], 0.50, False

        return crop_disease_list[0], 0.40, "healthy" in crop_disease_list[0].lower()

    def _fallback_prediction(
        self, features, crop_analysis, raw_predictions=None, raw_predicted_idx=None
    ):
        logger.info("Using fallback prediction")
        crop_name_h, crop_confidence_h, top5_crops = crop_analysis
        crop_name = crop_name_h

        unknown_threshold = 0.20

        if crop_confidence_h < unknown_threshold:
            crop_name = "Unknown"
            disease_name = "Unknown Crop"
            confidence = 0.0
            is_healthy = False
            top_5_predictions = [
                {
                    "class_name": "unknown",
                    "disease_name": "Unknown Crop",
                    "confidence": 0.0,
                }
                for _ in range(5)
            ]
            top_3_predictions = top_5_predictions[:3]
            all_conf = [0.0] * len(DISEASE_CLASSES)
            model_used = "unknown_crop"
        else:
            disease_name, confidence, is_healthy = self._detect_disease_from_features(
                features, crop_name_h
            )
            if confidence < CONFIDENCE_THRESHOLD:
                disease_name = "Inconclusive"
                model_used = "inconclusive"
            else:
                model_used = "image_analysis"

            [v for k, v in DISEASE_CLASSES.items() if v.startswith(crop_name_h)]
            top_5_predictions = self._build_disease_list_for_crop(
                crop_name_h, disease_name, features
            )
            top_3_predictions = top_5_predictions[:3]
            all_conf = [0.001] * len(DISEASE_CLASSES)
            if top_5_predictions:
                all_conf[0] = confidence

        result = {
            "success": True,
            "disease_name": disease_name,
            "crop_name": crop_name,
            "confidence": min(confidence, 0.98) if confidence else 0.0,
            "is_healthy": bool(is_healthy),
            "class_index": 0,
            "top_3_predictions": top_3_predictions,
            "top_5_predictions": top_5_predictions,
            "all_confidences": all_conf,
            "crop_confidence": round(crop_confidence_h, 3),
            "top_5_crops": [{"crop": c, "score": round(s, 1)} for c, s in top5_crops],
            "model_used": model_used,
        }

        if raw_predictions is not None and raw_predicted_idx is not None:
            result["raw_model_index"] = int(raw_predicted_idx)
            result["raw_model_confidences"] = raw_predictions[0].tolist()
            if self.class_names:
                raw_class_name = self.class_names.get(
                    raw_predicted_idx, f"Class_{raw_predicted_idx}"
                )
                result["raw_model_class"] = raw_class_name
                result["raw_model_disease"] = DISEASE_CLASSES.get(
                    raw_class_name, raw_class_name
                )
                result["raw_model_confidence"] = float(
                    raw_predictions[0][raw_predicted_idx]
                )
            top_n_idx = np.argsort(raw_predictions[0])[-5:][::-1]
            raw_top5 = []
            for idx in top_n_idx:
                cn = (
                    self.class_names.get(idx, f"Class_{idx}")
                    if self.class_names
                    else f"Class_{idx}"
                )
                dn = DISEASE_CLASSES.get(cn, cn)
                raw_top5.append(
                    {
                        "class_name": cn,
                        "disease_name": dn,
                        "confidence": float(raw_predictions[0][idx]),
                        "index": int(idx),
                    }
                )
            result["raw_model_top5"] = raw_top5

        return result

    def predict_crop(self, image_array):
        features = self._analyze_image(image_array)
        crop_name, crop_confidence, top5 = self._detect_crop_type(features)
        all_scores = {c: round(s, 1) for c, s in top5}
        total = sum(all_scores.values()) or 1
        all_pcts = {c: round(s / total * 100, 1) for c, s in all_scores.items()}
        return {
            "crop_name": crop_name,
            "confidence": round(crop_confidence, 3),
            "is_confident": crop_confidence >= CROP_CONFIDENCE_THRESHOLD,
            "top_candidates": [
                {"crop": c, "score": round(s, 1), "pct": all_pcts.get(c, 0)}
                for c, s in top5
            ],
            "all_scores": all_scores,
            "all_percentages": all_pcts,
        }

    def detect_crop(self, image_array):
        features = self._analyze_image(image_array)
        crop_name, crop_confidence, top5 = self._detect_crop_type(features)
        return {
            "crop_name": crop_name,
            "confidence": round(crop_confidence, 3),
            "top_candidates": [{"crop": c, "score": round(s, 1)} for c, s in top5],
            "image_features": {k: round(v, 1) for k, v in features.items()},
        }

    @staticmethod
    def audit_dataset(include_unknown=True):
        crops = {}
        for config_key, display_name in DISEASE_CLASSES.items():
            crop_name = display_name.split(" ")[0]
            if crop_name not in crops:
                crops[crop_name] = []
            crops[crop_name].append(
                {
                    "config_key": config_key,
                    "display_name": display_name,
                    "is_healthy": "healthy" in display_name.lower(),
                }
            )
        report = {
            "total_classes": len(DISEASE_CLASSES),
            "total_crops": len(crops),
            "crops": {},
        }
        for crop_name in sorted(crops.keys()):
            diseases = crops[crop_name]
            healthy_count = sum(1 for d in diseases if d["is_healthy"])
            disease_count = len(diseases) - healthy_count
            report["crops"][crop_name] = {
                "total_variants": len(diseases),
                "diseases": disease_count,
                "healthy_variants": healthy_count,
                "entries": diseases,
            }
        report["supported_crops"] = sorted(crops.keys())
        report["all_diseases"] = [
            d["display_name"]
            for c in sorted(crops.keys())
            for d in crops[c]
            if not d["is_healthy"]
        ]
        report["all_healthy"] = [
            d["display_name"]
            for c in sorted(crops.keys())
            for d in crops[c]
            if d["is_healthy"]
        ]
        return report

    def is_model_loaded(self):
        return self.model is not None
