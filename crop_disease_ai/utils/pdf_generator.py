import io
import os
from datetime import datetime

from reportlab.lib.colors import HexColor, grey
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from utils.config import ACCENT_COLOR, PRIMARY_COLOR, REPORTS_DIR, SECONDARY_COLOR


class PDFGenerator:
    def __init__(self):
        self.styles = self._create_styles()
        self.color_primary = HexColor(PRIMARY_COLOR)
        self.color_secondary = HexColor(SECONDARY_COLOR)
        self.color_accent = HexColor(ACCENT_COLOR)

    def _create_styles(self):
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(
            'CustomTitle', parent=styles['Title'],
            fontSize=24, textColor=HexColor(PRIMARY_COLOR),
            spaceAfter=20, alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        styles.add(ParagraphStyle(
            'CustomHeading', parent=styles['Heading1'],
            fontSize=16, textColor=HexColor(SECONDARY_COLOR),
            spaceBefore=15, spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        styles.add(ParagraphStyle(
            'SubHeading', parent=styles['Heading2'],
            fontSize=13, textColor=HexColor(PRIMARY_COLOR),
            spaceBefore=10, spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        styles.add(ParagraphStyle(
            'SmallText', parent=styles['Normal'],
            fontSize=9, textColor=grey,
            alignment=TA_CENTER
        ))
        styles.add(ParagraphStyle(
            'InfoText', parent=styles['Normal'],
            fontSize=10, spaceAfter=4,
            fontName='Helvetica',
            leading=14
        ))
        styles.add(ParagraphStyle(
            'LabelText', parent=styles['Normal'],
            fontSize=10, textColor=HexColor(SECONDARY_COLOR),
            fontName='Helvetica-Bold', spaceAfter=2
        ))
        styles.add(ParagraphStyle(
            'ValueText', parent=styles['Normal'],
            fontSize=11, spaceAfter=8,
            fontName='Helvetica'
        ))
        styles.add(ParagraphStyle(
            'RiskHigh', parent=styles['Normal'],
            fontSize=11, textColor=HexColor('#e74c3c'),
            fontName='Helvetica-Bold'
        ))
        styles.add(ParagraphStyle(
            'RiskMedium', parent=styles['Normal'],
            fontSize=11, textColor=HexColor('#e67e22'),
            fontName='Helvetica-Bold'
        ))
        styles.add(ParagraphStyle(
            'RiskLow', parent=styles['Normal'],
            fontSize=11, textColor=HexColor('#27ae60'),
            fontName='Helvetica-Bold'
        ))
        return styles

    def generate_report(self, output_path, data):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            topMargin=20*mm,
            bottomMargin=20*mm,
            leftMargin=15*mm,
            rightMargin=15*mm
        )

        story = []
        story.append(self._build_header(data))
        story.append(Spacer(1, 10*mm))

        if "image" in data and data["image"] is not None:
            story.append(self._build_image_section(data["image"]))
            story.append(Spacer(1, 5*mm))

        story.append(self._build_diagnosis_section(data))
        story.append(Spacer(1, 5*mm))

        story.append(self._build_severity_section(data))
        story.append(Spacer(1, 5*mm))

        if "weather" in data and data["weather"]:
            story.append(self._build_weather_section(data["weather"]))
            story.append(Spacer(1, 5*mm))

        story.append(self._build_treatment_section(data))
        story.append(Spacer(1, 5*mm))

        if "explanation" in data and data["explanation"]:
            story.append(self._build_explanation_section(data["explanation"]))

        story.append(self._build_footer(data))

        doc.build(story)
        return output_path

    def _build_header(self, data):
        elements = []
        elements.append(Paragraph(
            "AI-DRIVEN CROP DISEASE DIAGNOSIS REPORT",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            self.styles['SmallText']
        ))
        elements.append(Paragraph(
            f"Report ID: {data.get('report_id', 'N/A')}",
            self.styles['SmallText']
        ))

        header_data = [
            ["Farmer Name", data.get("farmer_name", "N/A")],
            ["Location", data.get("location", "N/A")],
            ["Crop Type", data.get("crop_name", "N/A")],
            ["Scan Date", data.get("scan_date", datetime.now().strftime("%Y-%m-%d %H:%M"))]
        ]
        header_table = Table(header_data, colWidths=[120, 320])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor(SECONDARY_COLOR)),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(header_table)
        return KeepTogether(elements)

    def _build_image_section(self, image_data):
        elements = []
        elements.append(Paragraph("Plant Image Analysis", self.styles['CustomHeading']))
        elements.append(Spacer(1, 3*mm))

        img_buffer = io.BytesIO()
        if hasattr(image_data, 'save'):
            image_data.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            img_width = 180*mm
            img_height = 120*mm
            elements.append(Image(img_buffer, width=img_width, height=img_height))
        else:
            elements.append(Paragraph("Image data not available", self.styles['InfoText']))

        return KeepTogether(elements)

    def _build_diagnosis_section(self, data):
        elements = []
        elements.append(Paragraph("Disease Diagnosis Results", self.styles['CustomHeading']))

        disease_name = data.get("disease_name", "Unknown")
        confidence = data.get("confidence", 0)
        is_healthy = "healthy" in disease_name.lower()

        if is_healthy:
            self.styles['RiskLow']
        elif data.get("severity", "") == "Severe":
            self.styles['RiskHigh']
        elif data.get("severity", "") == "Moderate":
            self.styles['RiskMedium']
        else:
            self.styles['RiskLow']

        diagnosis_data = [
            ["Disease Detected", disease_name],
            ["Confidence Score", f"{confidence*100:.2f}%"],
            ["Status", "Healthy Crop" if is_healthy else "Disease Detected"],
            ["Crop Type", data.get("crop_name", "N/A")]
        ]
        diag_table = Table(diagnosis_data, colWidths=[120, 320])
        diag_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor(SECONDARY_COLOR)),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(diag_table)

        return KeepTogether(elements)

    def _build_severity_section(self, data):
        elements = []
        elements.append(Paragraph("Severity Analysis", self.styles['CustomHeading']))

        severity = data.get("severity", "Unknown")
        infection_pct = data.get("infection_percentage", 0)
        risk_level = data.get("risk_level", "Unknown")

        severity_data = [
            ["Severity Level", severity],
            ["Infection Percentage", f"{infection_pct:.2f}%"],
            ["Risk Level", risk_level],
            ["Estimated Yield Impact", f"{data.get('yield_impact', 0)}%"]
        ]
        sev_table = Table(severity_data, colWidths=[120, 320])
        sev_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor(SECONDARY_COLOR)),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(sev_table)

        return KeepTogether(elements)

    def _build_weather_section(self, weather_data):
        elements = []
        elements.append(Paragraph("Weather Conditions at Time of Scan",
                                   self.styles['CustomHeading']))

        weather_info = [
            ["Temperature", f"{weather_data.get('temperature', 'N/A')}°C"],
            ["Humidity", f"{weather_data.get('humidity', 'N/A')}%"],
            ["Wind Speed", f"{weather_data.get('wind_speed', 'N/A')} m/s"],
            ["Condition", weather_data.get('weather_description', 'N/A').title()],
            ["Location", weather_data.get('location', 'N/A')]
        ]
        weather_table = Table(weather_info, colWidths=[120, 320])
        weather_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor(SECONDARY_COLOR)),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(weather_table)

        return KeepTogether(elements)

    def _build_treatment_section(self, data):
        elements = []
        elements.append(Paragraph("Treatment Recommendations",
                                   self.styles['CustomHeading']))

        treatment = data.get("treatment", {})

        if treatment:
            for category, recs in treatment.items():
                if recs and isinstance(recs, list):
                    category_name = category.replace("_", " ").title()
                    elements.append(Paragraph(category_name,
                                               self.styles['SubHeading']))
                    for _i, rec in enumerate(recs, 1):
                        elements.append(Paragraph(
                            f"&#8226; {rec}",
                            self.styles['InfoText']
                        ))
                    elements.append(Spacer(1, 3*mm))
        else:
            elements.append(Paragraph(
                "No specific treatment recommendations available.",
                self.styles['InfoText']
            ))

        return elements

    def _build_explanation_section(self, explanation):
        elements = []
        elements.append(Paragraph("AI Diagnostic Explanation",
                                   self.styles['CustomHeading']))

        rationale = explanation.get("prediction_rationale", [])
        if rationale:
            elements.append(Paragraph("Why this diagnosis was made:",
                                       self.styles['SubHeading']))
            for reason in rationale:
                elements.append(Paragraph(
                    f"&#8226; {reason}", self.styles['InfoText']
                ))

        confidence_analysis = explanation.get("confidence_analysis", {})
        if confidence_analysis:
            elements.append(Spacer(1, 3*mm))
            elements.append(Paragraph("Confidence Analysis:",
                                       self.styles['SubHeading']))
            confidence_items = [
                f"Overall Confidence: {confidence_analysis.get('overall_confidence', 0)}%",
                f"Confidence Rating: {confidence_analysis.get('confidence_rating', 'N/A')}",
                f"Margin over Second Prediction: {confidence_analysis.get('margin_over_second', 0)}%"
            ]
            for item in confidence_items:
                elements.append(Paragraph(
                    f"&#8226; {item}", self.styles['InfoText']
                ))

        return elements

    def _build_footer(self, data):
        elements = []
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph(
            "This report was generated by the AI-Driven Crop Disease Prediction System. "
            "The diagnosis is based on visual analysis and should be confirmed by "
            "a certified agricultural expert before implementing treatment.",
            ParagraphStyle('Footer', parent=self.styles['Normal'],
                           fontSize=8, textColor=grey, alignment=TA_CENTER,
                           fontName='Helvetica-Oblique')
        ))
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph(
            "© 2026 AI Crop Disease Management System. All rights reserved.",
            self.styles['SmallText']
        ))
        return elements

    def generate_report_bytes(self, data):
        from datetime import datetime
        report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        filename = f"disease_report_{report_id}.pdf"
        output_path = os.path.join(str(REPORTS_DIR), filename)
        self.generate_report(output_path, data)
        with open(output_path, "rb") as f:
            pdf_bytes = f.read()
        return pdf_bytes, filename, output_path
