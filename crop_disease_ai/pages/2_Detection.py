import sys
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.translator import init_i18n, t

st.set_page_config(
    page_title=t("app.title") + " - " + t("nav.detection"),
    page_icon="🔬",
    layout="wide",
)


def load_css():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(str(css_path)) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_models():
    from database.db_manager import DatabaseManager
    from utils.disease_knowledge_base import DiseaseKnowledgeBase
    from utils.explainable_ai import ExplainableAI
    from utils.image_processor import ImageProcessor
    from utils.model_handler import ModelHandler
    from utils.recommendation_engine import RecommendationEngine
    from utils.severity_analyzer import SeverityAnalyzer
    from utils.weather_api import WeatherAPI

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
    st.markdown(
        f"""
        <div class="main-header">
            <h1>{t("detection.title")}</h1>
            <p>{t("detection.subtitle")}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_step(number, title, status="pending"):
    status_icons = {"pending": "⏳", "active": "🔄", "done": "✅", "error": "❌"}
    icon = status_icons.get(status, "⏳")
    templates = {
        "done": f'<div class="detection-step completed"><div class="step-header"><div class="step-indicator done">{icon}</div><strong>{title}</strong></div></div>',
        "active": f'<div class="detection-step active"><div class="step-header"><div class="step-indicator active">{icon}</div><strong>{title}</strong></div><p style="color:var(--text-secondary);font-size:0.85rem;">Processing...</p></div>',
        "error": f'<div class="detection-step" style="border-color:#e53935;"><div class="step-header"><div class="step-indicator" style="background:#ffebee;color:#e53935;">{icon}</div><strong style="color:#e53935;">{title}</strong></div></div>',
    }
    return templates.get(
        status,
        f'<div class="detection-step"><div class="step-header"><div class="step-indicator pending">{icon}</div><strong style="color:var(--text-muted);">{title}</strong></div></div>',
    )


def render_image_preview(image_np):
    st.markdown('<div class="card" style="padding:1rem;">', unsafe_allow_html=True)
    st.markdown(
        "<h4 style='margin-bottom:0.5rem;font-size:0.95rem;'>📷 Image Preview</h4>",
        unsafe_allow_html=True,
    )
    display_img = (
        cv2.resize(image_np, (320, 320)) if image_np.shape[0] > 320 else image_np
    )
    if len(display_img.shape) == 3 and display_img.shape[-1] == 4:
        display_img = cv2.cvtColor(display_img, cv2.COLOR_RGBA2RGB)
    st.image(display_img, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)


def render_detection_settings():
    """Settings panel — purely input controls that write to session_state.

    No charts, no analytics, no prediction visualisation.  Only configuration
    toggles and threshold sliders.
    """
    with st.expander("⚙️ Detection Settings", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            threshold = st.slider(
                t("detection.confidence_threshold"),
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get("detection_settings", {}).get(
                    "confidence_threshold", 0.5
                ),
                step=0.05,
                help=t("detection.confidence_threshold_help"),
                key="detection_threshold_slider",
            )
        with col_b:
            model_variant = st.selectbox(
                t("detection.model_variant"),
                options=["default", "fast", "accurate"],
                index=0,
                help=t("detection.model_variant_help"),
                key="detection_model_variant",
            )

        col_c, col_d, col_e = st.columns(3)
        with col_c:
            enable_xai = st.toggle(
                t("detection.enable_xai"), value=True, key="detection_enable_xai"
            )
        with col_d:
            enable_severity = st.toggle(
                t("detection.enable_severity"),
                value=True,
                key="detection_enable_severity",
            )
        with col_e:
            enable_weather = st.toggle(
                t("detection.enable_weather"),
                value=True,
                key="detection_enable_weather",
            )

    st.session_state["detection_settings"] = {
        "confidence_threshold": threshold,
        "model_variant": model_variant,
        "enable_xai": enable_xai,
        "enable_severity": enable_severity,
        "enable_weather": enable_weather,
    }


def render_prediction_results(result, image_np, models):
    processor = models["processor"]
    severity_analyzer = models["severity"]
    knowledge_base = models["knowledge_base"]
    recommender = models["recommender"]
    xai = models["xai"]
    db = models["db"]
    settings = st.session_state.get("detection_settings", {})

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
    if settings.get("enable_weather", True):
        weather = models["weather"]
        loc = st.session_state.get("weather_location", "").strip()
        if loc and weather.is_configured():
            try:
                weather_data = weather.get_current_weather(loc)
            except Exception:
                weather_data = None

    recommendations = recommender.generate_recommendations(
        crop_name,
        disease_name,
        severity_result["severity"],
        infection_pct,
        weather_data,
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
        st.warning(t("detection.unknown_crop_warning"))

    if is_unknown_disease:
        st.markdown(
            f"""
            <div class="result-card" style="background:linear-gradient(135deg, #FB923C12, #FB923C06);
                 border:2px solid #FB923C;">
                <h2 style="color:#FB923C;">⚠️ Unknown Disease</h2>
                <p style="color:var(--text-secondary);">
                    Crop: <strong>{crop_name}</strong> ·
                    Status: <strong>Model confidence too low for reliable diagnosis</strong>
                </p>
            </div>
        """,
            unsafe_allow_html=True,
        )
        st.warning(
            "⚠️ **Model confidence too low for reliable diagnosis.** "
            "The AI model could not identify the disease with sufficient confidence. "
            "Consider uploading a clearer image or consulting an agricultural expert."
        )
        raw_top5 = result.get("raw_model_top5", [])
        if raw_top5:
            st.markdown(
                "<h4 style='margin-top:1rem;'>🔬 Raw Model Predictions (all low confidence)</h4>",
                unsafe_allow_html=True,
            )
            for i, pred in enumerate(raw_top5[:5]):
                pct = pred.get("confidence", 0) * 100
                st.markdown(f"{i + 1}. **{pred['disease_name']}**: {pct:.2f}%")
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

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {disease_color}15, {disease_color}08);
             border: 2px solid {disease_color}; border-radius: 16px; padding: 2rem;
             margin: 1rem 0;">
            <h2 style="color: {disease_color}; font-weight: 800; margin-bottom: 0.5rem;">
                {icon} {disease_name}
            </h2>
            <p style="font-size: 1.1rem; color: #555;">
                {t("detection.result_crop", crop=crop_name)} |
                {t("detection.result_confidence", confidence=f"{confidence * 100:.2f}")} |
                {t("detection.result_severity", severity=severity_result["severity"])}
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    if is_low_confidence:
        st.warning(
            t("detection.low_confidence_warning").format(confidence=confidence * 100)
        )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            t("detection.tab_analysis"),
            t("detection.tab_heatmap"),
            t("detection.tab_treatment"),
            t("detection.tab_explanation"),
            t("detection.tab_report"),
        ]
    )

    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            severity_val = severity_analyzer.get_severity_meter_value(
                severity_result["severity"]
            )
            st.markdown(
                f"<h4>{t('detection.severity_label', severity=severity_result['severity'])}</h4>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="severity-meter">
                    <div class="severity-meter-fill" style="width:{severity_val}%;
                         background:linear-gradient(90deg,{disease_color}88,{disease_color});"></div>
                </div>
                <p>{t("detection.infection_label", pct=f"{infection_pct:.1f}")}</p>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="info-box {"green" if is_healthy else "orange" if severity_result["severity"] == "Mild" else "red"}">
                    <strong>{t("detection.risk_level", level=severity_result["risk_level"])}</strong><br>
                    <strong>{t("detection.yield_impact", pct=yield_impact)}</strong><br>
                    <strong>{t("detection.treatment_urgency", urgency=severity_analyzer.get_treatment_urgency(severity_result["severity"]))}</strong>
                </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"**{t('detection.spread_estimation', estimation=severity_result['spread_estimation'])}**"
            )

            crop_confidence = result.get("crop_confidence", 0)
            if crop_confidence > 0:
                st.markdown(
                    f"""
                    <div style="margin: 0.5rem 0; padding: 0.5rem; background: #e8f5e9; border-radius: 8px;">
                        {t("detection.identified_crop", crop=crop_name)}
                        {t("detection.identified_confidence", pct=f"{crop_confidence * 100:.1f}")}
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            top5_crops = result.get("top_5_crops", [])
            if top5_crops and len(top5_crops) > 1:
                max_score = max(c["score"] for c in top5_crops)
                with st.expander(
                    t("detection.top_candidate_crops"), expanded=is_low_confidence
                ):
                    for _i, cp in enumerate(top5_crops):
                        bar_w = min(cp["score"] / max_score * 100, 100)
                        st.markdown(
                            f"""
                            <div style="margin:0.15rem 0;">
                                <div style="display:flex;justify-content:space-between;font-size:0.8rem;">
                                    <span>{cp["crop"]}</span>
                                    <span>{cp["score"]:.1f}</span>
                                </div>
                                <div class="severity-meter">
                                    <div class="severity-meter-fill" style="width:{bar_w}%;background:var(--primary);"></div>
                                </div>
                            </div>
                        """,
                            unsafe_allow_html=True,
                        )

            model_label = model_used.replace("_", " ").title()
            st.markdown(f"**{t('detection.method', method=model_label)}**")

            predictions_list = result.get(
                "top_5_predictions", result.get("top_3_predictions", [])
            )
            if predictions_list:
                st.markdown(f"**{t('detection.top_predictions')}**")
                top_colors = ["#2e7d32", "#1b5e20", "#555", "#777", "#999"]
                has_meaningful = False
                for i, pred in enumerate(predictions_list):
                    pct = pred.get("confidence", 0) * 100
                    if pct < 0.5:
                        continue
                    has_meaningful = True
                    bar_color = top_colors[i] if i < len(top_colors) else "#999"
                    st.markdown(
                        f"""
                        <div style="margin:0.2rem 0;">
                            <div style="display:flex;justify-content:space-between;font-size:0.85rem;">
                                <span><strong>{pred["disease_name"]}</strong></span>
                                <span><strong>{pct:.1f}%</strong></span>
                            </div>
                            <div class="severity-meter">
                                <div class="severity-meter-fill" style="width:{pct}%;background:{bar_color};"></div>
                            </div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                if not has_meaningful:
                    st.caption("No meaningful predictions available from the model.")

            raw_model = result.get("raw_model_top5")
            if raw_model:
                with st.expander(t("detection.raw_model_output"), expanded=False):
                    st.caption(t("detection.raw_model_caption"))
                    for pred in raw_model:
                        pct = pred["confidence"] * 100
                        st.markdown(
                            f"- **{pred['disease_name']}**: {pct:.1f}% (idx={pred['index']})"
                        )

            pred_quality = result.get("prediction_quality")
            if pred_quality:
                with st.expander(t("detection.prediction_quality"), expanded=False):
                    st.caption(t("detection.prediction_quality_caption"))
                    for err in pred_quality.get("validation_errors", []):
                        st.markdown(f"- ⚠️ {err}")
                    st.markdown(
                        f"- {t('detection.entropy', value=pred_quality.get('norm_entropy', 'N/A'))}"
                    )
                    st.markdown(
                        f"- {t('detection.margin', value=pred_quality.get('margin', 'N/A'))}"
                    )

        with col2:
            st.markdown(
                f"<h4>{t('detection.disease_info')}</h4>", unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <p><strong>{t("detection.description")}</strong> {disease_info.get("description", "N/A")[:300]}...</p>
                    <p style="margin-top: 0.5rem;"><strong>{t("detection.symptoms")}</strong></p>
                    <ul style="font-size: 0.9rem;">
                        {"".join(f"<li>{s}</li>" for s in disease_info.get("symptoms", [])[:4])}
                    </ul>
                    <p style="margin-top: 0.5rem;"><strong>{t("detection.favorable_conditions")}</strong><br>
                        {disease_info.get("favorable_conditions", "N/A")}</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"<h4 style='text-align: center;'>{t('detection.original_image')}</h4>",
                unsafe_allow_html=True,
            )
            display_img = cv2.resize(image_np, (224, 224))
            if display_img.shape[-1] == 4:
                display_img = cv2.cvtColor(display_img, cv2.COLOR_RGBA2RGB)
            elif len(display_img.shape) == 2:
                display_img = cv2.cvtColor(display_img, cv2.COLOR_GRAY2RGB)
            st.image(display_img, width="stretch")
        with col2:
            st.markdown(
                f"<h4 style='text-align: center;'>{t('detection.heatmap_title')}</h4>",
                unsafe_allow_html=True,
            )
            heatmap_rgb = (
                cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
                if heatmap.shape[-1] == 3 and len(heatmap.shape) == 3
                else heatmap
            )
            st.image(heatmap_rgb, width="stretch")
        with col3:
            st.markdown(
                f"<h4 style='text-align: center;'>{t('detection.overlay_view')}</h4>",
                unsafe_allow_html=True,
            )
            overlay_rgb = (
                cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
                if overlay.shape[-1] == 3
                else overlay
            )
            st.image(overlay_rgb, width="stretch")
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 1rem;">
                <p><strong>{t("detection.infected_area_label")}</strong> {infection_pct:.1f}% |
                <strong>{t("detection.severity_label_plain")}:</strong> {severity_result["severity"]}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with tab3:
        st.markdown(
            "<h4 style='margin-bottom:0.75rem;'>🧠 Grad-CAM Attention Map</h4>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color:var(--text-secondary);font-size:0.85rem;'>Shows which regions of the image influenced the model's decision most.</p>",
            unsafe_allow_html=True,
        )
        try:
            xai_model = models.get("xai")
            grad_model = getattr(xai_model, "model", None)
            if grad_model is None:
                grad_model = (
                    models["model"].model if hasattr(models["model"], "model") else None
                )
            if grad_model is not None:
                processed = models["processor"].prepare_for_model(image_np)
                class_idx = result.get("class_index", 0)
                heatmap_gradcam = xai_model.compute_gradcam(
                    grad_model, processed, class_idx
                )
                if heatmap_gradcam is not None:
                    display_img = cv2.resize(image_np, (224, 224))
                    if len(display_img.shape) == 3 and display_img.shape[-1] == 4:
                        display_img = cv2.cvtColor(display_img, cv2.COLOR_RGBA2RGB)
                    heatmap_colored = cv2.applyColorMap(
                        (heatmap_gradcam * 255).astype(np.uint8), cv2.COLORMAP_JET
                    )
                    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
                    overlay_gradcam = cv2.addWeighted(
                        display_img, 0.5, heatmap_colored, 0.5, 0
                    )
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(
                            "<p style='text-align:center;font-size:0.85rem;'>Original</p>",
                            unsafe_allow_html=True,
                        )
                        st.image(display_img, width="stretch")
                    with c2:
                        st.markdown(
                            "<p style='text-align:center;font-size:0.85rem;'>Grad-CAM Heatmap</p>",
                            unsafe_allow_html=True,
                        )
                        st.image(heatmap_colored, width="stretch")
                    with c3:
                        st.markdown(
                            "<p style='text-align:center;font-size:0.85rem;'>Overlay</p>",
                            unsafe_allow_html=True,
                        )
                        st.image(overlay_gradcam, width="stretch")
                    st.caption(
                        "Red regions = areas most influential to the model's prediction"
                    )
                else:
                    st.info(
                        "Grad-CAM could not be computed for this model architecture."
                    )
            else:
                st.info("Grad-CAM requires a Keras model with convolutional layers.")
        except Exception as e:
            st.info(f"Grad-CAM visualization unavailable: {e}")

    with tab4:
        recs = recommendations
        cat_icons = {
            "chemical_treatment": "🧪",
            "organic_treatment": "🌿",
            "fertilizer_suggestions": "🧫",
            "irrigation_guidance": "💧",
            "prevention_measures": "🛡️",
            "crop_management_tips": "📋",
        }
        cat_labels = {
            "chemical_treatment": t("treatment.chemical"),
            "organic_treatment": t("treatment.organic"),
            "fertilizer_suggestions": t("treatment.fertilizer"),
            "irrigation_guidance": t("treatment.irrigation"),
            "prevention_measures": t("treatment.prevention"),
            "crop_management_tips": t("treatment.management"),
        }

        st.markdown(
            f"""
            <div class="info-box {"orange" if recs.get("urgency", "").startswith("Medium") or recs.get("urgency", "").startswith("High") else "green"}">
                <strong>{t("detection.treatment_urgency_label", urgency=recs.get("urgency", "Normal"))}</strong>
            </div>
        """,
            unsafe_allow_html=True,
        )

        for cat_key, cat_icon in cat_icons.items():
            items = recs.get(cat_key, [])
            if items:
                expanded = cat_key in (
                    "chemical_treatment",
                    "organic_treatment",
                    "prevention_measures",
                )
                with st.expander(
                    f"{cat_icon} {cat_labels.get(cat_key, cat_key)}", expanded=expanded
                ):
                    for item in items:
                        st.markdown(f"- {item}")

    with tab5:
        st.markdown(
            f"<h4>{t('detection.explanation_title')}</h4>", unsafe_allow_html=True
        )
        for reason in explanation.get("prediction_rationale", []):
            st.markdown(f"- {reason}")

        st.markdown(
            f"<h4 style='margin-top: 1.5rem;'>{t('detection.confidence_analysis')}</h4>",
            unsafe_allow_html=True,
        )
        conf = explanation.get("confidence_analysis", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                t("detection.metric_confidence"),
                f"{conf.get('overall_confidence', 0):.1f}%",
            )
        with col2:
            st.metric(
                t("detection.metric_rating"), conf.get("confidence_rating", "N/A")
            )
        with col3:
            st.metric(
                t("detection.metric_margin"),
                f"{conf.get('margin_over_second', 0):.1f}%",
            )

        st.markdown(
            f"**{t('detection.reliability', reliability=conf.get('reliability', 'N/A'))}**"
        )

        similar = explanation.get("similar_diseases", [])
        if similar:
            st.markdown(
                f"<h4 style='margin-top: 1.5rem;'>{t('detection.similar_diseases')}</h4>",
                unsafe_allow_html=True,
            )
            for s in similar:
                st.markdown(
                    f"- **{s['disease_name']}** ({s['confidence']}%) — {s.get('similarity_reason', '')}"
                )

        st.markdown(
            f"<h4 style='margin-top: 1.5rem;'>{t('detection.model_interpretation')}</h4>",
            unsafe_allow_html=True,
        )
        interp = explanation.get("model_interpretation", {})
        st.markdown(
            f"**{t('detection.decision_path', path=interp.get('decision_path', 'N/A'))}**"
        )
        st.markdown(f"**{t('detection.primary_factors')}**")
        for factor in interp.get("primary_factors", []):
            st.markdown(f"- {factor}")

    # Report tab (was tab5 originally, now moved here)
    # We keep the report generation as a separate section
    st.markdown("---")
    st.markdown(f"<h4>{t('detection.generate_report')}</h4>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        farmer_name = st.text_input(
            t("detection.farmer_name"),
            value=st.session_state.get("farmer_name", ""),
        )
    with col2:
        farm_location = st.text_input(
            t("detection.farm_location"),
            value=st.session_state.get("farm_location", ""),
        )

    if st.button(t("detection.btn_generate_pdf"), type="primary", width="stretch"):
        with st.spinner(t("detection.generating_pdf")):
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
                    "farmer_name": farmer_name or t("common.not_specified"),
                    "location": farm_location or t("common.not_specified"),
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
                pdf_bytes, filename, pdf_path = pdf_gen.generate_report_bytes(
                    report_data
                )

                st.success(t("detection.report_generated", filename=filename))
                st.download_button(
                    label=t("detection.btn_download_pdf"),
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    width="stretch",
                )
            except Exception as e:
                st.error(t("detection.error_pdf", error=str(e)))

    st.markdown("---")
    if st.button(t("detection.btn_save_db"), width="stretch", type="secondary"):
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
            st.success(t("detection.db_success", id=pred_id))
            # Also append to in-memory history for analytics
            history_entry = {
                "id": pred_id,
                "crop_name": crop_name,
                "disease_name": disease_name,
                "confidence": confidence,
                "severity": severity_result["severity"],
                "infection_percentage": infection_pct,
                "risk_level": severity_result["risk_level"],
                "created_at": datetime.now().isoformat(),
            }
            history = st.session_state.get("prediction_history", [])
            history.insert(0, history_entry)
            st.session_state["prediction_history"] = history[:200]
        except Exception as e:
            st.error(t("detection.db_error", error=str(e)))


def main():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    init_i18n(st.session_state["language"])
    load_css()
    render_header()

    models_dir = Path(__file__).resolve().parent.parent / "models"
    model_file = models_dir / "plant_disease_model.h5"
    indices_file = models_dir / "class_indices.npy"
    if not model_file.exists() or not indices_file.exists():
        st.error("Model files missing. Please upload them to the models/ folder.")
        st.stop()

    models = get_models()

    # ── Left column: Image Upload / Capture ──
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <h3 style="margin-bottom: 1rem;">{t("detection.upload_section")}</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )

        input_method = st.radio(
            t("detection.input_method"),
            [t("detection.upload_image"), t("detection.capture_camera")],
            horizontal=True,
        )

        image_np = None
        uploaded_file = None

        if input_method == t("detection.upload_image"):
            uploaded_file = st.file_uploader(
                t("detection.choose_file"),
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
            img_file = st.camera_input(t("detection.capture_leaf"))
            if img_file:
                try:
                    processor = models["processor"]
                    image_bytes = img_file.getvalue()
                    image_np = processor.load_image_from_bytes(image_bytes)
                except Exception as e:
                    st.error(f"Failed to capture image: {e}")

        if image_np is not None:
            st.image(image_np, caption=t("detection.uploaded_image"), width="stretch")

    # ── Right column: Detection Settings + Predict ──
    with col_right:
        # Render the clean settings panel (purely configuration)
        render_detection_settings()

        if image_np is not None:
            processor = models["processor"]
            try:
                prepared = processor.prepare_for_model(image_np)
            except Exception as e:
                st.error(f"Image processing failed: {e}")
                prepared = None

            crop_pred = None
            crop_hint = None
            try:
                crop_pred = models["model"].predict_crop(prepared)
            except Exception as e:
                st.error(f"Crop detection failed: {e}")

            if crop_pred:
                st.markdown(f"**{t('detection.crop_candidates')}**")
                for _cp in crop_pred["top_candidates"][:5]:
                    bar_w = min(_cp["pct"], 100)
                    st.markdown(
                        f"""
                        <div style="margin: 0.2rem 0;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                                <span>{_cp["crop"]}</span>
                                <span>{_cp["pct"]:.1f}%</span>
                            </div>
                            <div class="severity-meter">
                                <div class="severity-meter-fill" style="width: {bar_w}%;
                                     background: {"#2e7d32" if _cp["crop"] == crop_pred["crop_name"] else "#888"};"></div>
                            </div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                if not crop_pred["is_confident"]:
                    st.warning(
                        t(
                            "detection.crop_low_confidence",
                            confidence=f"{crop_pred['confidence'] * 100:.1f}",
                        )
                    )
                    manual_crop = st.selectbox(
                        f"**{t('detection.select_crop_manual')}**",
                        [crop_pred["crop_name"]]
                        + [
                            c
                            for c in sorted(models["model"].SUPPORTED_CROPS)
                            if c != crop_pred["crop_name"]
                        ],
                        index=0,
                    )
                    crop_hint = manual_crop
                else:
                    st.success(
                        t(
                            "detection.crop_confident",
                            crop=crop_pred["crop_name"],
                            confidence=f"{crop_pred['confidence'] * 100:.1f}",
                        )
                    )
            else:
                st.info(
                    "Crop prediction unavailable; detection will use the disease model fallback."
                )

            st.session_state["weather_location"] = st.text_input(
                t("detection.weather_location"),
                placeholder=t("detection.weather_placeholder"),
                value=st.session_state.get("weather_location", ""),
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button(t("detection.btn_detect"), type="primary", width="stretch"):
                with st.spinner(t("detection.analyzing")):
                    try:
                        result = models["model"].predict(prepared, crop_hint=crop_hint)
                        if result["success"]:
                            render_prediction_results(result, image_np, models)
                        else:
                            st.error(t("detection.error_prediction"))
                    except Exception as e:
                        st.error(t("detection.error_detection", error=str(e)))
                        import traceback

                        st.error(traceback.format_exc())
        else:
            st.info(t("detection.hint_upload"))

    if image_np is not None and "last_result" not in st.session_state:
        st.info(t("detection.hint_detect"))


if __name__ == "__main__":
    if "last_result" in st.session_state:
        del st.session_state["last_result"]
    main()
