import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import cv2
from PIL import Image
import io
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.translator import t

st.set_page_config(page_title=t("app.title") + " - " + t("nav.detection"), page_icon="🔬", layout="wide")
from utils.translator import init_i18n, t

st.set_page_config(page_title="Disease Detection - Crop Disease AI", page_icon="🔬", layout="wide")


def load_css():
    with open("assets/style.css") as f:
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
        "db": DatabaseManager()
    }


def render_header():
    st.markdown(f"""
        <div class="main-header">
            <h1>{t("detection.title")}</h1>
            <p>{t("detection.subtitle")}</p>
            <h1>{t('detection.title')}</h1>
            <p>{t('detection.subtitle')}</p>
        </div>
    """, unsafe_allow_html=True)


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
        weather_data = weather.get_current_weather(loc)

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
        "yield_impact": yield_impact
    }

    if is_unknown_crop:
        st.warning(t("detection.unknown_crop_warning"))

    disease_color = "#888"
    icon = "❓"
    if is_low_confidence:
        disease_color = "#e67e22"
        icon = "⚠️"
    elif is_healthy:
        disease_color = "#2ecc71"
        icon = "✅"
    else:
        disease_color = severity_result["color"]
        icon = severity_result.get("icon", "🔬")

    severity_label = t("severity." + severity_result["severity"].lower()) if severity_result["severity"].lower() in ["healthy", "mild", "moderate", "severe"] else severity_result["severity"]

    st.markdown(f"""
        <div style="background: linear-gradient(135deg, {disease_color}15, {disease_color}08);
             border: 2px solid {disease_color}; border-radius: 16px; padding: 2rem;
             margin: 1rem 0;">
            <h2 style="color: {disease_color}; font-weight: 800; margin-bottom: 0.5rem;">
                {icon} {disease_name}
            </h2>
            <p style="font-size: 1.1rem; color: #555;">
                {t("detection.identified_crop").format(crop=crop_name, conf=confidence*100)} |
                {t("detection.metric_confidence")}: <strong>{confidence*100:.2f}%</strong> |
                {t("detection.severity_label").format(severity=severity_label)}
                {t('detection.result_crop', crop=crop_name)} |
                {t('detection.result_confidence', confidence=f'{confidence*100:.2f}')} |
                {t('detection.result_severity', severity=severity_result['severity'])}
            </p>
    """, unsafe_allow_html=True)

    if is_low_confidence:
        st.warning(t("detection.low_confidence_warning").format(confidence=confidence*100))
        st.warning(t("detection.low_confidence_warning", confidence=f"{confidence*100:.1f}"))

    st.markdown("</div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [t("detection.tab_analysis"), t("detection.tab_heatmap"), t("detection.tab_treatment"),
         t("detection.tab_xai"), t("detection.tab_report")]
        [t("detection.tab_analysis"), t("detection.tab_heatmap"), t("detection.tab_treatment"), t("detection.tab_explanation"), t("detection.tab_report")]
    )

    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            severity_val = severity_analyzer.get_severity_meter_value(severity_result["severity"])
            st.markdown(f"""
                <h4>{t("detection.severity_label").format(severity=severity_label)}</h4>
                <h4>{t('detection.severity_label', severity=severity_result['severity'])}</h4>
                <div class="severity-meter">
                    <div class="severity-meter-fill" style="width: {severity_val}%;
                         background: linear-gradient(90deg, {disease_color}88, {disease_color});"></div>
                </div>
                <p>{t("detection.infection_label").format(pct=infection_pct)}</p>
                <p>{t('detection.infection_label', pct=f'{infection_pct:.1f}')}</p>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="info-box {'green' if is_healthy else 'orange' if severity_result['severity']=='Mild' else 'red'}">
                    <strong>{t("detection.risk_level")}</strong> {t("severity.risk_" + severity_result['risk_level'].lower())}<br>
                    <strong>{t("detection.yield_impact").format(pct=yield_impact)}</strong><br>
                    <strong>{t("detection.treatment_urgency").format(urgency=t("severity.urgency_" + severity_result['severity'].lower()))}</strong>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**{t('detection.spread_estimation').format(estimation=t('severity.spread_' + severity_result['severity'].lower()))}**")
                    <strong>{t('detection.risk_level', level=severity_result['risk_level'])}</strong><br>
                    <strong>{t('detection.yield_impact', pct=yield_impact)}</strong><br>
                    <strong>{t('detection.treatment_urgency', urgency=severity_analyzer.get_treatment_urgency(severity_result['severity']))}</strong>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**{t('detection.spread_estimation', estimation=severity_result['spread_estimation'])}**")

            crop_confidence = result.get("crop_confidence", 0)
            top5_crops = result.get("top_5_crops", [])

            if crop_confidence > 0:
                crop_conf_pct = crop_confidence * 100
                st.markdown(f"""
                    <div style="margin: 0.5rem 0; padding: 0.5rem; background: #e8f5e9; border-radius: 8px;">
                        <strong>{t("detection.identified_crop").format(crop=crop_name, conf=crop_conf_pct)}</strong>
                        <strong>{t('detection.identified_crop', crop=crop_name)}</strong>
                        {t('detection.identified_confidence', pct=f'{crop_conf_pct:.0f}')}
                    </div>
                """, unsafe_allow_html=True)

            if top5_crops and len(top5_crops) > 1:
                max_score = max(c["score"] for c in top5_crops)
                with st.expander(t("detection.top_candidate_crops"), expanded=is_low_confidence):
                    for i, cp in enumerate(top5_crops):
                        bar_w = min(cp["score"] / max_score * 100, 100)
                        st.markdown(f"""
                            <div style="margin: 0.2rem 0;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                                    <span>{cp['crop']}</span>
                                    <span>{cp['score']:.1f}</span>
                                </div>
                                <div class="severity-meter">
                                    <div class="severity-meter-fill" style="width: {bar_w}%;
                                         background: #2e7d32;"></div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

            model_label = model_used.replace("_", " ").title()
            st.markdown(f"**{t('detection.method').format(method=model_label)}**")
            st.markdown(f"**{t('detection.method', method=model_label)}**")

            st.markdown(f"**{t('detection.top_predictions')}**")
            predictions_list = result.get("top_5_predictions", result.get("top_3_predictions", []))
            top_5_colors = ["#2e7d32", "#1b5e20", "#555", "#777", "#999"]
            for i, pred in enumerate(predictions_list):
                pct = pred["confidence"] * 100
                if pct < 0.5:
                    continue
                bar_color = top_5_colors[i] if i < len(top_5_colors) else "#999"
                crop_tag = pred.get("disease_name", "").split(" ")[0] if " " in pred.get("disease_name", "") else ""
                st.markdown(f"""
                    <div style="margin: 0.3rem 0;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                            <span><strong>{pred['disease_name']}</strong></span>
                            <span><strong>{pct:.1f}%</strong></span>
                        </div>
                        <div class="severity-meter">
                            <div class="severity-meter-fill" style="width: {pct}%;
                                 background: {bar_color};"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            raw_model = result.get("raw_model_top5")
            if raw_model:
                with st.expander(t("detection.raw_model_output"), expanded=False):
                    st.caption(t("detection.raw_model_caption"))
                    for pred in raw_model:
                        pct = pred["confidence"] * 100
                        st.markdown(f"- **{pred['disease_name']}**: {pct:.1f}% (idx={pred['index']})")

            pred_quality = result.get("prediction_quality")
            if pred_quality:
                with st.expander(t("detection.prediction_quality"), expanded=False):
                    st.caption(t("detection.prediction_quality_caption"))
                    for err in pred_quality.get("validation_errors", []):
                        st.markdown(f"- ⚠️ {err}")
                    st.markdown(f"- {t('detection.entropy', value=pred_quality.get('norm_entropy', 'N/A'))}")
                    st.markdown(f"- {t('detection.margin', value=pred_quality.get('margin', 'N/A'))}")

        with col2:
            st.markdown(f"<h4>{t('detection.disease_info')}</h4>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="dashboard-card">
                    <p><strong>{t('detection.description')}</strong> {disease_info.get('description', 'N/A')[:300]}...</p>
                    <p style="margin-top: 0.5rem;"><strong>{t('detection.symptoms')}</strong></p>
                    <ul style="font-size: 0.9rem;">
                        {''.join(f'<li>{s}</li>' for s in disease_info.get('symptoms', [])[:4])}
                    </ul>
                    <p style="margin-top: 0.5rem;"><strong>{t('detection.favorable_conditions')}</strong><br>
                        {disease_info.get('favorable_conditions', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<h4 style='text-align: center;'>{t('detection.original_image')}</h4>", unsafe_allow_html=True)
            display_img = cv2.resize(image_np, (224, 224))
            if display_img.shape[-1] == 4:
                display_img = cv2.cvtColor(display_img, cv2.COLOR_RGBA2RGB)
            elif len(display_img.shape) == 2:
                display_img = cv2.cvtColor(display_img, cv2.COLOR_GRAY2RGB)
            st.image(display_img, width='stretch')

        with col2:
            st.markdown(f"<h4 style='text-align: center;'>{t('detection.heatmap_view')}</h4>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align: center;'>{t('detection.heatmap_title')}</h4>", unsafe_allow_html=True)
            heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB) if heatmap.shape[-1] == 3 and len(heatmap.shape) == 3 else heatmap
            st.image(heatmap_rgb, width='stretch')

        with col3:
            st.markdown(f"<h4 style='text-align: center;'>{t('detection.overlay_view')}</h4>", unsafe_allow_html=True)
            overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB) if overlay.shape[-1] == 3 else overlay
            st.image(overlay_rgb, width='stretch')

        st.markdown(f"""
            <div style="text-align: center; margin-top: 1rem;">
                <p><strong>{t('detection.infected_area').format(pct=infection_pct)}</strong> |
                <strong>{t('detection.severity_label').format(severity=severity_label)}</strong></p>
                <p><strong>{t('detection.infected_area_label')}</strong> {infection_pct:.1f}% | <strong>{t('detection.severity_label_plain')}:</strong> {severity_result['severity']}</p>
            </div>
        """, unsafe_allow_html=True)

    with tab3:
        recs = recommendations
        cat_icons = {"chemical_treatment": "🧪", "organic_treatment": "🌿",
                     "fertilizer_suggestions": "🧫", "irrigation_guidance": "💧",
                     "prevention_measures": "🛡️", "crop_management_tips": "📋"}
        cat_keys_map = {"chemical_treatment": "chemical", "organic_treatment": "organic",
                        "fertilizer_suggestions": "fertilizer", "irrigation_guidance": "irrigation",
                        "prevention_measures": "prevention", "crop_management_tips": "management"}
        cat_labels = {"chemical_treatment": t("treatment.chemical"),
                      "organic_treatment": t("treatment.organic"),
                      "fertilizer_suggestions": t("treatment.fertilizer"),
                      "irrigation_guidance": t("treatment.irrigation"),
                      "prevention_measures": t("treatment.prevention"),
                      "crop_management_tips": t("treatment.management")}

        st.markdown(f"""
            <div class="info-box {'orange' if recs.get('urgency','').startswith('Medium') or recs.get('urgency','').startswith('High') else 'green'}">
                <strong>{t('detection.urgency').format(urgency=recs.get('urgency', 'Normal'))}</strong>
        cat_labels = {"chemical_treatment": t("detection.treatment_chemical"),
                      "organic_treatment": t("detection.treatment_organic"),
                      "fertilizer_suggestions": t("detection.treatment_fertilizer"),
                      "irrigation_guidance": t("detection.treatment_irrigation"),
                      "prevention_measures": t("detection.treatment_prevention"),
                      "crop_management_tips": t("detection.treatment_management")}

        st.markdown(f"""
            <div class="info-box {'orange' if recs.get('urgency','').startswith('Medium') or recs.get('urgency','').startswith('High') else 'green'}">
                <strong>{t('detection.treatment_urgency_label', urgency=recs.get('urgency', 'Normal'))}</strong>
            </div>
        """, unsafe_allow_html=True)

        for cat_key, cat_icon in cat_icons.items():
            items = recs.get(cat_key, [])
            if items:
                with st.expander(f"{cat_icon} {cat_labels.get(cat_key, cat_key)}", expanded=(cat_key in ["chemical_treatment", "organic_treatment"])):
                    for item in items:
                        st.markdown(f"- {item}")

    with tab4:
        st.markdown(f"<h4>{t('detection.why_diagnosis')}</h4>", unsafe_allow_html=True)
        st.markdown(f"<h4>{t('detection.explanation_title')}</h4>", unsafe_allow_html=True)
        for reason in explanation.get("prediction_rationale", []):
            st.markdown(f"- {reason}")

        st.markdown(f"<h4 style='margin-top: 1.5rem;'>{t('detection.confidence_analysis')}</h4>", unsafe_allow_html=True)
        conf = explanation.get("confidence_analysis", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t("detection.metric_confidence"), f"{conf.get('overall_confidence', 0):.1f}%")
        with col2:
            st.metric(t("detection.metric_rating"), conf.get("confidence_rating", "N/A"))
        with col3:
            st.metric(t("detection.metric_margin"), f"{conf.get('margin_over_second', 0):.1f}%")

        st.markdown(f"**{t('detection.reliability').format(reliability=conf.get('reliability', 'N/A'))}**")
        st.markdown(f"**{t('detection.reliability', reliability=conf.get('reliability', 'N/A'))}**")

        similar = explanation.get("similar_diseases", [])
        if similar:
            st.markdown(f"<h4 style='margin-top: 1.5rem;'>{t('detection.similar_diseases')}</h4>", unsafe_allow_html=True)
            for s in similar:
                st.markdown(f"- **{s['disease_name']}** ({s['confidence']}%) - {s.get('similarity_reason', '')}")

        st.markdown(f"<h4 style='margin-top: 1.5rem;'>{t('detection.model_interpretation')}</h4>", unsafe_allow_html=True)
        interp = explanation.get("model_interpretation", {})
        st.markdown(f"**{t('detection.decision_path').format(path=interp.get('decision_path', 'N/A'))}**")
        st.markdown(f"**{t('detection.decision_path', path=interp.get('decision_path', 'N/A'))}**")
        st.markdown(f"**{t('detection.primary_factors')}**")
        for factor in interp.get("primary_factors", []):
            st.markdown(f"- {factor}")

    with tab5:
        st.markdown(f"<h4>{t('detection.generate_report')}</h4>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            farmer_name = st.text_input(t("detection.farmer_name"), value=st.session_state.get("farmer_name", ""))
        with col2:
            farm_location = st.text_input(t("detection.farm_location"), value=st.session_state.get("farm_location", ""))

        if st.button(t("detection.btn_generate_pdf"), type="primary", width='stretch'):
            with st.spinner(t("detection.spinner_pdf")):
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
                        "yield_impact": yield_impact
                    }

                    pdf_bytes, filename, pdf_path = pdf_gen.generate_report_bytes(report_data)

                    st.success(t("detection.pdf_success").format(filename=filename))
                    st.success(t("detection.report_generated", filename=filename))
                    st.download_button(
                        label=t("detection.btn_download_pdf"),
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        width='stretch'
                    )
                except Exception as e:
                    st.error(t("detection.pdf_error").format(error=str(e)))
                    st.error(t("detection.error_pdf", error=str(e)))

        st.markdown("---")
        if st.button(t("detection.btn_save_db"), width='stretch', type="secondary"):
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
                    treatment_recommendations=recommendations
                )
                st.success(t("detection.db_success").format(id=pred_id))
            except Exception as e:
                st.error(t("detection.db_error").format(error=str(e)))
                st.success(t("detection.saved_to_db", id=pred_id))
            except Exception as e:
                st.error(t("detection.error_save", error=str(e)))


def main():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    init_i18n(st.session_state["language"])
    load_css()
    render_header()

    models = get_models()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"""
            <div class="dashboard-card">
                <h3 style="margin-bottom: 1rem;">{t("detection.upload_section")}</h3>
            </div>
        """, unsafe_allow_html=True)

        input_method = st.radio(t("detection.input_method"), [t("detection.upload_image"), t("detection.capture_camera")], horizontal=True)
                <h3 style="margin-bottom: 1rem;">{t('detection.upload_section')}</h3>
            </div>
        """, unsafe_allow_html=True)

        input_method = st.radio(t("detection.input_method"), [t("detection.upload_option"), t("detection.camera_option")], horizontal=True)

        image_np = None
        uploaded_file = None

        if input_method == t("detection.upload_image"):
            uploaded_file = st.file_uploader(
                t("detection.choose_file"),
        if input_method == t("detection.upload_option"):
            uploaded_file = st.file_uploader(
                t("detection.file_uploader"),
                type=["jpg", "jpeg", "png", "webp", "tiff"],
                label_visibility="collapsed"
            )
            if uploaded_file:
                processor = models["processor"]
                is_valid, msg = processor.validate_image(uploaded_file)
                if not is_valid:
                    st.error(msg)
                    uploaded_file = None
                else:
                    image_np = processor.load_image(uploaded_file)

        else:
            img_file = st.camera_input(t("detection.capture_leaf"))
            img_file = st.camera_input(t("detection.camera_label"))
            if img_file:
                from utils.image_processor import ImageProcessor
                processor = ImageProcessor()
                image_bytes = img_file.getvalue()
                image_np = processor.load_image_from_bytes(image_bytes)

        if image_np is not None:
            st.image(image_np, caption=t("detection.uploaded_image"), width='stretch')
            st.image(image_np, caption=t("detection.uploaded_caption"), width='stretch')

    with col2:
        st.markdown(f"""
            <div class="dashboard-card">
                <h3 style="margin-bottom: 1rem;">{t("detection.settings_section")}</h3>
                <h3 style="margin-bottom: 1rem;">{t('detection.settings_section')}</h3>
            </div>
        """, unsafe_allow_html=True)

        if image_np is not None:
            processor = models["processor"]
            prepared = processor.prepare_for_model(image_np)
            crop_pred = models["model"].predict_crop(prepared)

            st.markdown(f"**{t('detection.crop_candidates')}**")
            for cp in crop_pred["top_candidates"][:5]:
                bar_w = min(cp["pct"], 100)
                st.markdown(f"""
                    <div style="margin: 0.2rem 0;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                            <span>{cp['crop']}</span>
                            <span>{cp['pct']:.1f}%</span>
                        </div>
                        <div class="severity-meter">
                            <div class="severity-meter-fill" style="width: {bar_w}%;
                                 background: {"#2e7d32" if cp['crop'] == crop_pred['crop_name'] else "#888"};"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            if not crop_pred["is_confident"]:
                st.warning(
                    t("detection.crop_confidence_warning").format(confidence=crop_pred['confidence']*100)
                )
                manual_crop = st.selectbox(
                    t("detection.manual_crop_select"),
                st.warning(t("detection.crop_low_confidence", confidence=f"{crop_pred['confidence']*100:.1f}"))
                manual_crop = st.selectbox(
                    f"**{t('detection.select_crop_manual')}**",
                    [crop_pred["crop_name"]] + [c for c in sorted(models["model"].SUPPORTED_CROPS) if c != crop_pred["crop_name"]],
                    index=0
                )
                crop_hint = manual_crop
            else:
                st.success(t("detection.detected_crop").format(crop=crop_pred['crop_name'], confidence=crop_pred['confidence']*100))
                crop_hint = None

            st.session_state["weather_location"] = st.text_input(
                t("detection.enter_weather"),
                placeholder=t("detection.weather_hint"),
                st.success(t("detection.crop_confident", crop=crop_pred['crop_name'], confidence=f"{crop_pred['confidence']*100:.1f}"))
                crop_hint = None

            st.session_state["weather_location"] = st.text_input(
                t("detection.weather_location"),
                placeholder=t("detection.weather_placeholder"),
                value=st.session_state.get("weather_location", "")
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button(t("detection.btn_detect"), type="primary", width='stretch'):
                with st.spinner(t("detection.analysis_spinner")):
                with st.spinner(t("detection.analyzing")):
                    try:
                        result = models["model"].predict(prepared, crop_hint=crop_hint)

                        if result["success"]:
                            render_prediction_results(result, image_np, models)
                        else:
                            st.error(t("detection.error_prediction"))
                    except Exception as e:
                        st.error(t("detection.error_detection").format(error=str(e)))
                        import traceback
                        st.error(traceback.format_exc())
        else:
            st.info(t("detection.hint_upload"))

    if image_np is not None and "last_result" not in st.session_state:
        st.info(t("detection.hint_detect"))
                            st.error(t("detection.error_model"))
                    except Exception as e:
                        st.error(t("detection.error_detection", error=str(e)))
                        import traceback
                        st.error(traceback.format_exc())
        else:
            st.info(t("detection.waiting_upload"))

    if image_np is not None and "last_result" not in st.session_state:
        st.info(t("detection.waiting_click"))


if __name__ == "__main__":
    if "last_result" in st.session_state:
        del st.session_state["last_result"]
    main()
