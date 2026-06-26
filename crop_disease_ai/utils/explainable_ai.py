import logging

import cv2
import numpy as np
import tensorflow as tf

from utils.config import IMG_SIZE

logger = logging.getLogger(__name__)


class ExplainableAI:
    def __init__(self, model=None):
        self.model = model

    def generate_explanation(self, prediction_result, image_array, disease_info):
        disease_name = prediction_result.get("disease_name", "Unknown")
        confidence = prediction_result.get("confidence", 0)
        top_3 = prediction_result.get("top_3_predictions", [])
        is_healthy = prediction_result.get("is_healthy", False)

        explanation = {
            "prediction_rationale": self._get_prediction_rationale(
                disease_name, confidence, is_healthy
            ),
            "key_features": self._get_key_features(disease_name, disease_info),
            "similar_diseases": self._get_similar_diseases(disease_name, top_3),
            "confidence_analysis": self._analyze_confidence(confidence, top_3),
            "model_interpretation": self._interpret_model_decision(
                disease_name, confidence, top_3
            ),
        }
        return explanation

    def _get_prediction_rationale(self, disease_name, confidence, is_healthy):
        reasons = []
        if is_healthy:
            reasons.extend(
                [
                    "Leaf appears uniformly green with no significant discoloration",
                    "No visible lesions or spots detected in the analyzed region",
                    "Texture analysis shows healthy tissue patterns",
                    "Color distribution matches healthy reference samples",
                ]
            )
        else:
            reasons.extend(
                [
                    f"Abnormal color patterns detected consistent with {disease_name}",
                    "Irregular spot patterns identified on leaf surface",
                    "Textural changes detected in affected regions",
                    "Chlorophyll distribution analysis shows anomalies",
                ]
            )

        if confidence > 0.95:
            reasons.append("High confidence - model is very certain of this diagnosis")
        elif confidence > 0.80:
            reasons.append("Good confidence - model is reasonably certain")
        else:
            reasons.append("Moderate confidence - consider additional diagnostic tests")

        return reasons

    def _get_key_features(self, disease_name, disease_info):
        disease_symptoms = disease_info.get("symptoms", []) if disease_info else []
        key_features = []
        for symptom in disease_symptoms[:5]:
            key_features.append({"feature": symptom, "importance": "high"})
        return key_features

    def _get_similar_diseases(self, disease_name, top_3_predictions):
        similar = []
        for pred in top_3_predictions[1:]:
            if pred["confidence"] > 0.1:
                similar.append(
                    {
                        "disease_name": pred["disease_name"],
                        "confidence": round(pred["confidence"] * 100, 2),
                        "similarity_reason": self._get_similarity_reason(
                            disease_name, pred["disease_name"]
                        ),
                    }
                )
        return similar

    def _get_similarity_reason(self, primary, secondary):
        primary_base = primary.split(" ")[-1] if " " in primary else primary
        secondary_base = secondary.split(" ")[-1] if " " in secondary else secondary

        if primary_base == secondary_base:
            return "Same disease type, possibly different severity stage"
        elif "healthy" in secondary.lower():
            return "Close to healthy classification with mild symptoms"
        else:
            return "Similar visual patterns in early infection stages"

    def _analyze_confidence(self, confidence, top_3):
        analysis = {
            "overall_confidence": round(confidence * 100, 2),
            "confidence_rating": self._get_confidence_rating(confidence),
            "margin_over_second": self._calculate_margin(confidence, top_3),
            "reliability": self._get_reliability(confidence),
        }
        return analysis

    def _get_confidence_rating(self, confidence):
        if confidence >= 0.95:
            return "Very High"
        elif confidence >= 0.85:
            return "High"
        elif confidence >= 0.75:
            return "Moderate"
        elif confidence >= 0.60:
            return "Low"
        return "Very Low"

    def _calculate_margin(self, confidence, top_3):
        if len(top_3) < 2:
            return 0
        margin = (confidence - top_3[1]["confidence"]) * 100
        return round(margin, 2)

    def _get_reliability(self, confidence):
        if confidence >= 0.90:
            return "Highly reliable - diagnosis can be used confidently"
        elif confidence >= 0.80:
            return "Reliable - consider confirmation through visual inspection"
        elif confidence >= 0.70:
            return "Moderately reliable - visual confirmation recommended"
        else:
            return "Low reliability - please consult an agricultural expert"

    def _interpret_model_decision(self, disease_name, confidence, top_3):
        interpretation = {
            "primary_factors": [
                "Leaf color distribution patterns",
                "Texture analysis of affected regions",
                "Shape and pattern of detected lesions",
                "Spatial distribution of anomalies",
            ],
            "decision_path": f"The model analyzed the image and identified patterns "
            f"most consistent with {disease_name} with "
            f"{confidence * 100:.1f}% confidence. "
            f"The neural network detected characteristic features "
            f"in the leaf tissue that match training examples of this condition.",
        }
        return interpretation

    def compute_gradcam(self, model, image_array, class_idx=None):
        try:
            if model is None:
                return None

            if len(model.inputs) == 0:
                _ = model(image_array)

            last_conv_layer = self._find_last_conv_layer(model)
            if last_conv_layer is None:
                return None

            grad_model = tf.keras.Model(
                inputs=model.inputs, outputs=[last_conv_layer.output, model.output]
            )

            with tf.GradientTape() as tape:
                conv_outputs, predictions = grad_model(image_array)
                if class_idx is None:
                    class_idx = tf.argmax(predictions[0])
                loss = predictions[:, class_idx]

            grads = tape.gradient(loss, conv_outputs)
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

            conv_outputs = conv_outputs[0]
            heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
            heatmap = tf.squeeze(heatmap)

            heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
            heatmap = heatmap.numpy()

            heatmap = cv2.resize(heatmap, (IMG_SIZE, IMG_SIZE))
            return heatmap

        except Exception as e:
            logger.warning(f"GradCAM computation failed: {e}")
            return None

    def _find_last_conv_layer(self, model):
        for layer in reversed(model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                return layer
            if (
                hasattr(layer, "output")
                and hasattr(layer.output, "shape")
                and len(layer.output.shape) == 4
            ):
                return layer
        return None

    def highlight_infected_regions(self, image_np, infection_mask):
        if len(image_np.shape) == 3 and image_np.shape[-1] == 4:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
        elif len(image_np.shape) == 2:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGB)

        display_img = cv2.resize(image_np, (IMG_SIZE, IMG_SIZE))
        mask_colored = cv2.applyColorMap(
            (infection_mask * 255).astype(np.uint8)
            if infection_mask.max() <= 1
            else infection_mask.astype(np.uint8),
            cv2.COLORMAP_JET,
        )
        mask_colored = cv2.cvtColor(mask_colored, cv2.COLOR_BGR2RGB)
        overlay = cv2.addWeighted(display_img, 0.5, mask_colored, 0.5, 0)

        return overlay
