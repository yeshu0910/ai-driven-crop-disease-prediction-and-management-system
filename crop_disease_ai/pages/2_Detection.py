import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import cv2
from PIL import Image
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def load_css():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(str(css_path)) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_models():
    from utils.model_handler import ModelHandler
    from utils.image_processor import ImageProcessor
    from utils.severity_analyzer import SeverityAnalyzer
    from utils.disease_knowledge_base import DiseaseKnowledgeBase
    from utils.recommendation_engine import RecommendationEngine
    from utils.explainable_ai import ExplainableAI
    from utils.weather_api import WeatherAPI
    from database.db_manager import DatabaseManager
    return {
        "model": ModelHandler(),
        "processor": ImageProcessor(),
        "severity": SeverityAnalyzer(),
        "knowledge_base": DiseaseKnowledgeBase(),
        "recommender": RecommendationEngine(),
        "xai": ExplainableAI(),
        "weather": WeatherAPI(),
        "db": DatabaseManager(),
    }


def render_header():
    st.markdown("""
        <div class="main-header">
            <h1>🔬 AI Disease Detection</h1>
            <p>Upload a leaf image to detect diseases with AI-powered analysis</p>
        </div>
    """, unsafe_allow_html=True)


def render_step(number, title, status="pending"):
    status_icons = {"pending": "⏳", "active": "🔄", "done": "✅", "error": "❌"}
    icon = status_icons.get(status, "⏳")
    cls = status
    if status == "done":
        return f'<div class="detection-step completed"><div class="step-header"><div class="step-indicator done">{icon}</div><strong>{title}</strong></div></div>'
    elif status == "active":
        return f'<div class="detection-step active"><div class="step-header"><div class="step-indicator active">{icon}</div><strong>{title}</strong></div><p style="color:var(--text-secondary);font-size:0.85rem;">Processing...</p></div>'
    elif status == "error":
        return f'<div class="detection-step" style="border-color:#e53935;"><div class="step-header"><div class="step-indicator" style="background:#ffebee;color:#e53935;">{icon}</div><strong style="color:#e53935;">{title}</strong></div></div>'
    else:
        return f'<div class="detection-step"><div class="step-header"><div class="step-indicator pending">{icon}</div><strong style="color:var(--text-muted);">{title}</strong></div></div>'


def render_image_preview(image_np):
    st.markdown('<div class="card" style="padding:1rem;">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-bottom:0.5rem;font-size:0.95rem;'>📷 Image Preview</h4>", unsafe_allow_html=True)
    display_img = cv2.resize(image_np, (320, 320)) if image_np.shape[0] > 320 else image_np
    if len(display_img.shape) == 3 and display_img.shape[-1] == 4:
        display_img = cv2.cvtColor(display_img, cv2.COLOR_RGBA2RGB)
    st.image(display_img, width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)


def render_prediction_results(result, image_np, models):
    processor = models["processor"]
    severity_analyzer = models["severity"]
    knowledge_base = models["knowledge_base"]
    recommender = models["recommender"]
    xai = models["xai"]
    db = models["db"]

    disease_name = result["disease_name"]
    crop_name = result["crop_name"]
    confidence = result["confidence"]
    is_healthy = result["is_healthy"]
    is_low_confidence = result.get("is_low_confidence", False)
    model_used = result.get("model_used", "unknown")
    is_unknown_crop = crop_name == "Unknown"
    is_unknown_disease = model_used in ("unknown_disease", "unknown_crop")

    infection_pct, infection_mask = processor.analyze_infection_area(image_np)
    severity_result = severity_analyzer.analyze(infection_pct, disease_name, confidence)

    disease_info = knowledge_base.get_disease_info(disease_name)

    weather_data = None
    weather = models["weather"]
    loc = st.session_state.get("weather_location", "").strip()
    if loc and weather.is_configured():
        try:
            weather_data = weather.get_current_weather(loc)
        except Exception:
            weather_data = None

    recommendations = recommender.generate_recommendations(
        crop_name, disease_name, severity_result["severity"],
        infection_pct, weather_data
    )

    explanation = xai.generate_explanation(result, image_np, disease_info)
    overlay, heatmap, thresh = processor.generate_heatmap(image_np, infection_mask)
    yield_impact = severity_analyzer.calculate_yield_impact(
        severity_result["severity"], crop_name
    )

    st.session_state["last_result"] = {
        "disease_name": disease_name,
        "crop_name": crop_name,
        "confidence": confidence,
        "severity": severity_result["severity"],
        "infection_percentage": infection_pct,
        "risk_level": severity_result["risk_level"],
        "image": image_np,
        "treatment": recommendations,
        "weather": weather_data,
        "explanation": explanation,
        "yield_impact": yield_impact,
    }

    if is_unknown_crop:
        st.markdown("""
            <div class="result-card" style="background:linear-gradient(135deg, #FB923C12, #FB923C06);
                 border:2px solid #FB923C;">
                <h2 style="color:#FB923C;">⚠️ Unknown Crop</h2>
                <p style="color:var(--text-secondary);">
                    Status: <strong>Could not identify the crop type</strong>
                </p>
            </div>
        """, unsafe_allow_html=True)
        st.warning("Could not identify the crop type with sufficient confidence. Consider uploading a clearer image or selecting the crop manually.")
        return

    if is_unknown_disease:
        st.markdown("""
            <div class="result-card" style="background:linear-gradient(135deg, #FB923C12, #FB923C06);
                 border:2px solid #FB923C;">
                <h2 style="color:#FB923C;">⚠️ Unknown Disease</h2>
                <p style="color:var(--text-secondary);">
                    Crop: <strong>{}</strong> ·
                    Status: <strong>Model confidence too low for reliable diagnosis</strong>
                </p>
            </div>
        """.format(crop_name), unsafe_allow_html=True)
        st.warning("⚠️ **Model confidence too low for reliable diagnosis.** The AI model could not identify the disease with sufficient confidence. Consider uploading a clearer image or consulting an agricultural expert.")
        raw_top5 = result.get("raw_model_top5", [])
        if raw_top5:
            st.markdown("<h4 style='margin-top:1rem;'>🔬 Raw Model Predictions (all low confidence)</h4>", unsafe_allow_html=True)
            for i, pred in enumerate(raw_top5[:5]):
                pct = pred.get("confidence", 0) * 100
                st.markdown(f"{i+1}. **{pred['disease_name']}**: {pct:.2f}%")
        return

    if is_healthy:
        disease_color = "#2DD4BF"
        icon = "✅"
    elif is_low_confidence:
        disease_color = "#FB923C"
        icon = "⚠️"
    else:
        disease_color = severity_result["color"]
        icon = severity_result.get("icon", "🔬")

    st.markdown(f"""
        <div class="result-card" style="background:linear-gradient(135deg, {disease_color}12, {disease_color}06);
             border:2px solid {disease_color};">
            <h2 style="color:{disease_color};">{icon} {disease_name}</h2>
            <p style="color:var(--text-secondary);">
                Crop: <strong>{crop_name}</strong> ·
                Confidence: <strong>{confidence*100:.2f}%</strong> ·
                Severity: <strong>{severity_result['severity']}</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)

    if is_low_confidence:
        st.warning(f"⚠️ **Low Confidence Prediction** — Confidence is {confidence*100:.1f}%. Please upload a clearer image for better accuracy.")

    tabs = st.tabs(["📊 Analysis", "🔬 Heatmap", "🧠 Grad-CAM", "💊 Treatment", "🤖 AI Explanation", "📄 Report"])

    with tabs[0]:
        col1, col2 = st.columns([1, 1])
        with col1:
            severity_val = severity_analyzer.get_severity_meter_value(severity_result["severity"])
            st.markdown(f"<h4>Severity: {severity_result['severity']}</h4>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="severity-meter">
                    <div class="severity-meter-fill" style="width:{severity_val}%;
                         background:linear-gradient(90deg,{disease_color}88,{disease_color});"></div>
                </div>
                <p style="color:var(--text-secondary);font-size:0.9rem;">Infection: {infection_pct:.1f}%</p>
            """, unsafe_allow_html=True)

            box_class = "green" if is_healthy else ("orange" if severity_result["severity"] == "Mild" else "red")
            st.markdown(f"""
                <div class="info-box {box_class}">
                    <strong>Risk Level:</strong> {severity_result['risk_level']}<br>
                    <strong>Yield Impact:</strong> ~{yield_impact}%<br>
                    <strong>Treatment Urgency:</strong> {severity_analyzer.get_treatment_urgency(severity_result['severity'])}
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**Spread Estimation:** {severity_result['spread_estimation']}")

            crop_confidence = result.get("crop_confidence", 0)
            if crop_confidence > 0:
                st.markdown(f"""
                    <div style="margin:0.5rem 0;padding:0.5rem 0.75rem;background:var(--primary-bg);
                         border-radius:var(--radius-sm);font-size:0.9rem;">
                        <strong>Identified Crop:</strong> {crop_name} ({crop_confidence*100:.0f}% confidence)
                    </div>
                """, unsafe_allow_html=True)

            # Top 5 crops
            top5_crops = result.get("top_5_crops", [])
            if top5_crops and len(top5_crops) > 1:
                max_score = max(c["score"] for c in top5_crops)
                with st.expander("🌾 Top Candidate Crops", expanded=is_low_confidence):
                    for cp in top5_crops:
                        bar_w = min(cp["score"] / max_score * 100, 100) if max_score > 0 else 0
                        st.markdown(f"""
                            <div style="margin:0.15rem 0;">
                                <div style="display:flex;justify-content:space-between;font-size:0.8rem;">
                                    <span>{cp['crop']}</span>
                                    <span>{cp['score']:.1f}</span>
                                </div>
                                <div class="severity-meter">
                                    <div class="severity-meter-fill" style="width:{bar_w}%;background:var(--primary);"></div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

            model_label = model_used.replace("_", " ").title()
            st.markdown(f"**Method:** {model_label}")

            # Top 5 predictions
            st.markdown("<h5 style='margin-top:1rem;'>🏆 Top Predictions</h5>", unsafe_allow_html=True)
            predictions_list = result.get("top_5_predictions", result.get("top_3_predictions", []))
            top_colors = ["#2e7d32", "#1b5e20", "#555", "#777", "#999"]
            has_meaningful = False
            for i, pred in enumerate(predictions_list):
                pct = pred.get("confidence", 0) * 100
                if pct < 0.5:
                    continue
                has_meaningful = True
                bar_color = top_colors[i] if i < len(top_colors) else "#999"
                st.markdown(f"""
                    <div style="margin:0.2rem 0;">
                        <div style="display:flex;justify-content:space-between;font-size:0.85rem;">
                            <span><strong>{pred['disease_name']}</strong></span>
                            <span><strong>{pct:.1f}%</strong></span>
                        </div>
                        <div class="severity-meter">
                            <div class="severity-meter-fill" style="width:{pct}%;background:{bar_color};"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            if not has_meaningful:
                st.caption("No meaningful predictions available from the model.")

            # Raw model output
            raw_model = result.get("raw_model_top5")
            if raw_model:
                with st.expander("Raw Model Output (before validation)", expanded=False):
                    st.caption("Neural network predictions before crop consistency check")
                    for pred in raw_model:
                        pct = pred["confidence"] * 100
                        st.markdown(f"- **{pred['disease_name']}**: {pct:.1f}% (idx={pred['index']})")

            pred_quality = result.get("prediction_quality")
            if pred_quality:
                with st.expander("Prediction Quality Metrics", expanded=False):
                    for err in pred_quality.get("validation_errors", []):
                        st.markdown(f"- ⚠️ {err}")
                    st.markdown(f"- Entropy: {pred_quality.get('norm_entropy', 'N/A')}")
                    st.markdown(f"- Margin: {pred_quality.get('margin', 'N/A')}")

        with col2:
            st.markdown("<h4>Disease Information</h4>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="card">
                    <p style="font-size:0.9rem;color:var(--text-secondary);">{disease_info.get('description', 'No description available.')[:300]}</p>
                    <p style="margin-top:0.5rem;font-weight:600;">Symptoms:</p>
                    <ul style="font-size:0.85rem;color:var(--text-secondary);padding-left:1.25rem;">
                        {''.join(f'<li style="margin:0.2rem 0;">{s}</li>' for s in disease_info.get('symptoms', [])[:4])}
                    </ul>
                    <p style="margin-top:0.5rem;font-size:0.85rem;"><strong>Favorable Conditions:</strong><br>{disease_info.get('favorable_conditions', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)

    with tabs[1]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<h5 style='text-align:center;'>Original Image</h5>", unsafe_allow_html=True)
            display_img = cv2.resize(image_np, (224, 224))
            if display_img.shape[-1] == 4:
                display_img = cv2.cvtColor(display_img, cv2.COLOR_RGBA2RGB)
            elif len(display_img.shape) == 2:
                display_img = cv2.cvtColor(display_img, cv2.COLOR_GRAY2RGB)
            st.image(display_img, width='stretch')
        with col2:
            st.markdown("<h5 style='text-align:center;'>Infection Heatmap</h5>", unsafe_allow_html=True)
            heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB) if heatmap.shape[-1] == 3 and len(heatmap.shape) == 3 else heatmap
            st.image(heatmap_rgb, width='stretch')
        with col3:
            st.markdown("<h5 style='text-align:center;'>Overlay View</h5>", unsafe_allow_html=True)
            overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB) if overlay.shape[-1] == 3 else overlay
            st.image(overlay_rgb, width='stretch')
        st.markdown(f"""
            <div style="text-align:center;margin-top:0.75rem;font-size:0.9rem;color:var(--text-secondary);">
                <strong>Infected Area:</strong> {infection_pct:.1f}% of leaf surface |
                <strong>Severity:</strong> {severity_result['severity']}
            </div>
        """, unsafe_allow_html=True)

    with tabs[2]:
        st.markdown("<h4 style='margin-bottom:0.75rem;'>🧠 Grad-CAM Attention Map</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color:var(--text-secondary);font-size:0.85rem;'>Shows which regions of the image influenced the model's decision most.</p>", unsafe_allow_html=True)
        try:
            xai_model = models.get("xai")
            grad_model = getattr(xai_model, 'model', None)
            if grad_model is None:
                grad_model = models["model"].model if hasattr(models["model"], 'model') else None
            if grad_model is not None:
                processed = models["processor"].prepare_for_model(image_np)
                class_idx = result.get("class_index", 0)
                heatmap_gradcam = xai_model.compute_gradcam(grad_model, processed, class_idx)
                if heatmap_gradcam is not None:
                    display_img = cv2.resize(image_np, (224, 224))
                    if len(display_img.shape) == 3 and display_img.shape[-1] == 4:
                        display_img = cv2.cvtColor(display_img, cv2.COLOR_RGBA2RGB)
                    heatmap_colored = cv2.applyColorMap(
                        (heatmap_gradcam * 255).astype(np.uint8), cv2.COLORMAP_JET
                    )
                    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
                    overlay_gradcam = cv2.addWeighted(display_img, 0.5, heatmap_colored, 0.5, 0)
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown("<p style='text-align:center;font-size:0.85rem;'>Original</p>", unsafe_allow_html=True)
                        st.image(display_img, width='stretch')
                    with c2:
                        st.markdown("<p style='text-align:center;font-size:0.85rem;'>Grad-CAM Heatmap</p>", unsafe_allow_html=True)
                        st.image(heatmap_colored, width='stretch')
                    with c3:
                        st.markdown("<p style='text-align:center;font-size:0.85rem;'>Overlay</p>", unsafe_allow_html=True)
                        st.image(overlay_gradcam, width='stretch')
                    st.caption("Red regions = areas most influential to the model's prediction")
                else:
                    st.info("Grad-CAM could not be computed for this model architecture.")
            else:
                st.info("Grad-CAM requires a Keras model with convolutional layers.")
        except Exception as e:
            st.info(f"Grad-CAM visualization unavailable: {e}")

    with tabs[3]:
        recs = recommendations
        cat_icons = {"chemical_treatment": "🧪", "organic_treatment": "🌿",
                     "fertilizer_suggestions": "🧫", "irrigation_guidance": "💧",
                     "prevention_measures": "🛡️", "crop_management_tips": "📋"}
        cat_labels = {"chemical_treatment": "Chemical Treatment",
                      "organic_treatment": "Organic Treatment",
                      "fertilizer_suggestions": "Fertilizer Suggestions",
                      "irrigation_guidance": "Irrigation Guidance",
                      "prevention_measures": "Prevention Measures",
                      "crop_management_tips": "Crop Management Tips"}

        urg = recs.get("urgency", "Normal")
        urg_color = "green" if "No" in urg or "Low" in urg else "orange"
        st.markdown(f"""
            <div class="info-box {urg_color}" style="margin-bottom:0.75rem;">
                <strong>Urgency:</strong> {urg}
            </div>
        """, unsafe_allow_html=True)

        for cat_key, cat_icon in cat_icons.items():
            items = recs.get(cat_key, [])
            if items:
                expanded = cat_key in ("chemical_treatment", "organic_treatment", "prevention_measures")
                with st.expander(f"{cat_icon} {cat_labels.get(cat_key, cat_key)}", expanded=expanded):
                    for item in items:
                        st.markdown(f"- {item}")

    with tabs[4]:
        st.markdown("<h4 style='margin-bottom:0.75rem;'>Why This Diagnosis Was Made</h4>", unsafe_allow_html=True)
        for reason in explanation.get("prediction_rationale", []):
            st.markdown(f"- {reason}")

        st.markdown("<h4 style='margin-top:1.25rem;margin-bottom:0.75rem;'>Confidence Analysis</h4>", unsafe_allow_html=True)
        conf = explanation.get("confidence_analysis", {})
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Confidence", f"{conf.get('overall_confidence', 0):.1f}%")
        with c2:
            st.metric("Rating", conf.get("confidence_rating", "N/A"))
        with c3:
            st.metric("Margin", f"{conf.get('margin_over_second', 0):.1f}%")
        st.markdown(f"**Reliability:** {conf.get('reliability', 'N/A')}")

        similar = explanation.get("similar_diseases", [])
        if similar:
            st.markdown("<h4 style='margin-top:1.25rem;'>Similar Diseases Considered</h4>", unsafe_allow_html=True)
            for s in similar:
                st.markdown(f"- **{s['disease_name']}** ({s['confidence']}%) — {s.get('similarity_reason', '')}")

        interp = explanation.get("model_interpretation", {})
        st.markdown("<h4 style='margin-top:1.25rem;'>Model Interpretation</h4>", unsafe_allow_html=True)
        st.markdown(f"**Decision Path:** {interp.get('decision_path', 'N/A')}")
        st.markdown("**Primary Factors Considered:**")
        for factor in interp.get("primary_factors", []):
            st.markdown(f"- {factor}")

    with tabs[5]:
        st.markdown("<h4 style='margin-bottom:0.75rem;'>Generate Diagnostic Report</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            farmer_name = st.text_input("Farmer Name", value=st.session_state.get("farmer_name", ""))
        with c2:
            farm_location = st.text_input("Farm Location", value=st.session_state.get("farm_location", ""))

        if st.button("📄 Generate PDF Report", type="primary", width='stretch'):
            with st.spinner("Generating PDF report..."):
                try:
                    from utils.pdf_generator import PDFGenerator
                    pdf_gen = PDFGenerator()
                    report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    pil_img = Image.fromarray(
                        cv2.cvtColor(cv2.resize(image_np, (224, 224)), cv2.COLOR_BGR2RGB)
                        if len(image_np.shape) == 3 and image_np.shape[-1] == 3
                        else image_np
                    )
                    report_data = {
                        "report_id": report_id,
                        "farmer_name": farmer_name or "Not Specified",
                        "location": farm_location or "Not Specified",
                        "crop_name": crop_name,
                        "disease_name": disease_name,
                        "confidence": confidence,
                        "severity": severity_result["severity"],
                        "infection_percentage": infection_pct,
                        "risk_level": severity_result["risk_level"],
                        "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "image": pil_img,
                        "treatment": recommendations,
                        "weather": weather_data,
                        "explanation": explanation,
                        "yield_impact": yield_impact,
                    }
                    pdf_bytes, filename, pdf_path = pdf_gen.generate_report_bytes(report_data)
                    st.success(f"✅ Report generated: {filename}")
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        width='stretch'
                    )
                except Exception as e:
                    st.error(f"Failed to generate PDF: {e}")

        st.markdown("---")
        if st.button("💾 Save to Database", width='stretch', type="secondary"):
            try:
                pred_id = db.save_prediction(
                    farmer_id=1,
                    image_path="webcam_capture",
                    crop_name=crop_name,
                    disease_name=disease_name,
                    confidence=confidence,
                    severity=severity_result["severity"],
                    infection_percentage=infection_pct,
                    risk_level=severity_result["risk_level"],
                    weather_data=weather_data,
                    treatment_recommendations=recommendations,
                )
                st.success(f"✅ Saved to database (ID: {pred_id})")
            except Exception as e:
                st.error(f"Failed to save: {e}")


def main():
    load_css()
    render_header()

    models = get_models()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("<h3 class='gradient-text-primary'>📷 Upload Image</h3>", unsafe_allow_html=True)

        input_method = st.radio(
            "Choose input method:",
            ["Upload Image", "Capture from Camera"],
            horizontal=True,
        )

        image_np = None
        uploaded_file = None

        if input_method == "Upload Image":
            uploaded_file = st.file_uploader(
                "Choose a leaf image...",
                type=["jpg", "jpeg", "png", "webp", "tiff"],
                label_visibility="collapsed",
            )
            if uploaded_file:
                processor = models["processor"]
                is_valid, msg = processor.validate_image(uploaded_file)
                if not is_valid:
                    st.error(msg)
                    uploaded_file = None
                else:
                    try:
                        image_np = processor.load_image(uploaded_file)
                    except Exception as e:
                        st.error(f"Failed to load image: {e}")
                        image_np = None
        else:
            img_file = st.camera_input("Capture leaf image")
            if img_file:
                try:
                    from utils.image_processor import ImageProcessor
                    processor = ImageProcessor()
                    image_bytes = img_file.getvalue()
                    image_np = processor.load_image_from_bytes(image_bytes)
                except Exception as e:
                    st.error(f"Failed to capture image: {e}")

        if image_np is not None:
            render_image_preview(image_np)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("<h3 class='gradient-text-primary'>⚙️ Detection Settings</h3>", unsafe_allow_html=True)

        if image_np is not None:
            processor = models["processor"]
            try:
                prepared = processor.prepare_for_model(image_np)
            except Exception as e:
                st.error(f"Image processing failed: {e}")
                prepared = None

            crop_pred = None
            crop_hint = None

            if prepared is not None:
                try:
                    crop_pred = models["model"].predict_crop(prepared)
                except Exception as e:
                    st.error(f"Crop detection failed: {e}")

            if crop_pred:
                st.markdown("**Detected Crop Candidates:**")
                for cp in crop_pred["top_candidates"][:5]:
                    bar_w = min(cp["pct"], 100)
                    is_best = cp["crop"] == crop_pred["crop_name"]
                    st.markdown(f"""
                        <div style="margin:0.15rem 0;">
                            <div style="display:flex;justify-content:space-between;font-size:0.85rem;">
                                <span>{cp['crop']}</span>
                                <span>{cp['pct']:.1f}%</span>
                            </div>
                            <div class="severity-meter">
                                <div class="severity-meter-fill" style="width:{bar_w}%;
                                     background:{"var(--primary)" if is_best else "var(--border)"};"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                if not crop_pred["is_confident"]:
                    st.warning(f"Crop confidence ({crop_pred['confidence']*100:.1f}%) below 95% threshold. Select crop manually or accept auto-detected crop.")
                    crop_list = sorted(models["model"].SUPPORTED_CROPS)
                    manual_crop = st.selectbox(
                        "**Select Crop (manual override):**",
                        [crop_pred["crop_name"]] + [c for c in crop_list if c != crop_pred["crop_name"]],
                        index=0,
                    )
                    crop_hint = manual_crop
                else:
                    st.success(f"**Detected Crop:** {crop_pred['crop_name']} ({crop_pred['confidence']*100:.1f}% confidence)")

            st.session_state["weather_location"] = st.text_input(
                "Weather Location (e.g., city name)",
                placeholder="e.g., Mumbai, Delhi, Pune",
                value=st.session_state.get("weather_location", ""),
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🔍 Detect Disease", type="primary", width='stretch'):
                with st.spinner("🔬 Analyzing image with AI model..."):
                    try:
                        result = models["model"].predict(prepared, crop_hint=crop_hint)
                        if result["success"]:
                            render_prediction_results(result, image_np, models)
                        else:
                            st.error("Model prediction failed. Please try again.")
                    except Exception as e:
                        st.error(f"Error during detection: {e}")
        else:
            st.info("👆 Upload or capture an image to start detection")
        st.markdown("</div>", unsafe_allow_html=True)

    if image_np is not None and "last_result" not in st.session_state:
        st.info("Click **'Detect Disease'** to analyze the image")


if __name__ == "__main__":
    if "last_result" in st.session_state:
        del st.session_state["last_result"]
    main()
