"""
Medical PDF Report Generator
Generates professional medical reports with QR codes and Grad-CAM heatmaps
"""

import os
import io
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import qrcode
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Image,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Colors
PRIMARY_COLOR = colors.HexColor("#2563EB")
SECONDARY_COLOR = colors.HexColor("#06B6D4")
SUCCESS_COLOR = colors.HexColor("#10B981")
DANGER_COLOR = colors.HexColor("#EF4444")
WARNING_COLOR = colors.HexColor("#F59E0B")
GRAY_COLOR = colors.HexColor("#6B7280")
LIGHT_GRAY = colors.HexColor("#F3F4F6")


def generate_pdf_report(
    patient_name: str,
    patient_age: Optional[int],
    patient_gender: Optional[str],
    prediction: str,
    confidence: float,
    probability_normal: float,
    probability_pneumonia: float,
    gradcam_image_path: Optional[str] = None,
    doctor_name: str = "Dr. AI System",
    doctor_notes: Optional[str] = None,
    hospital_name: str = "PneumoVision AI Medical Center",
) -> str:
    """
    Generate a professional medical PDF report.
    
    Args:
        patient_name: Name of the patient
        patient_age: Age of patient
        patient_gender: Gender of patient
        prediction: Prediction result (Normal/Pneumonia)
        confidence: Confidence score
        probability_normal: Probability of normal
        probability_pneumonia: Probability of pneumonia
        gradcam_image_path: Path to Grad-CAM heatmap image
        doctor_name: Name of reviewing doctor
        doctor_notes: Additional doctor notes
        hospital_name: Hospital/Institution name
    
    Returns:
        Path to generated PDF file
    """
    # Generate unique filename
    pdf_filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
    pdf_path = REPORTS_DIR / pdf_filename
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=PRIMARY_COLOR,
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=PRIMARY_COLOR,
        spaceBefore=12,
        spaceAfter=6,
    )
    
    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#374151"),
        spaceAfter=4,
    )
    
    result_style = ParagraphStyle(
        "ResultStyle",
        parent=styles["Normal"],
        fontSize=18,
        textColor=SUCCESS_COLOR if prediction == "Normal" else DANGER_COLOR,
        alignment=TA_CENTER,
        spaceBefore=10,
        spaceAfter=10,
    )
    
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=GRAY_COLOR,
        alignment=TA_CENTER,
        spaceBefore=20,
    )
    
    # Build document content
    elements = []
    
    # Header with logo placeholder
    header_data = [[
        Paragraph(f"<b>{hospital_name}</b>", title_style),
    ]]
    header_table = Table(header_data, colWidths=[doc.width])
    header_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(header_table)
    
    elements.append(HRFlowable(
        width="100%",
        thickness=2,
        color=PRIMARY_COLOR,
        spaceAfter=12,
    ))
    
    # Report title
    elements.append(Paragraph("AI-Powered Chest X-Ray Analysis Report", heading_style))
    elements.append(Spacer(1, 6))
    
    # Report info
    report_info = [
        [f"Report ID: {pdf_filename.replace('.pdf', '')}", f"Date: {datetime.utcnow().strftime('%B %d, %Y')}"],
        [f"Generated: {datetime.utcnow().strftime('%H:%M:%S UTC')}", ""],
    ]
    info_table = Table(report_info, colWidths=[doc.width * 0.5, doc.width * 0.5])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), GRAY_COLOR),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 12))
    
    # Patient Information Section
    elements.append(Paragraph("Patient Information", heading_style))
    
    patient_data = [
        ["Name:", patient_name, "Age:", str(patient_age) if patient_age else "N/A"],
        ["Gender:", patient_gender or "N/A", "Report Type:", "Chest X-Ray (AI Analysis)"],
    ]
    patient_table = Table(patient_data, colWidths=[1*inch, 2*inch, 1*inch, 2*inch])
    patient_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), GRAY_COLOR),
        ("TEXTCOLOR", (2, 0), (2, -1), GRAY_COLOR),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 12))
    
    # Analysis Results Section
    elements.append(Paragraph("Analysis Results", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=SECONDARY_COLOR, spaceAfter=6))
    
    # Prediction result
    result_text = f"<b>{prediction}</b>"
    elements.append(Paragraph(f"Diagnosis: {result_text}", result_style))
    elements.append(Spacer(1, 8))
    
    # Confidence scores
    confidence_color = SUCCESS_COLOR if confidence > 0.9 else WARNING_COLOR if confidence > 0.7 else DANGER_COLOR
    
    scores_data = [
        ["Metric", "Value"],
        ["Confidence Score", f"{confidence:.2%}"],
        ["Probability - Normal", f"{probability_normal:.2%}"],
        ["Probability - Pneumonia", f"{probability_pneumonia:.2%}"],
        ["AI Model", "EfficientNetB0 (Transfer Learning)"],
    ]
    scores_table = Table(scores_data, colWidths=[2.5*inch, 2.5*inch])
    scores_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
        ("TEXTCOLOR", (1, 1), (1, 1), confidence_color),
        ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GRAY),
        ("GRID", (0, 0), (-1, -1), 1, colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(scores_table)
    elements.append(Spacer(1, 12))
    
    # Grad-CAM Heatmap
    if gradcam_image_path and os.path.exists(gradcam_image_path):
        elements.append(Paragraph("Grad-CAM Heatmap Analysis", heading_style))
        try:
            img = PILImage.open(gradcam_image_path)
            img_width, img_height = img.size
            
            # Scale image to fit page
            max_width = doc.width * 0.7
            if img_width > max_width:
                ratio = max_width / img_width
                img_width = max_width
                img_height = img_height * ratio
            
            grad_img = Image(gradcam_image_path, width=img_width, height=img_height)
            elements.append(grad_img)
            elements.append(Paragraph(
                "<i>Heatmap showing regions of interest for AI decision</i>",
                ParagraphStyle("Caption", parent=normal_style, fontSize=8, textColor=GRAY_COLOR, alignment=TA_CENTER),
            ))
        except Exception as e:
            logger.error(f"Failed to add Grad-CAM image to PDF: {str(e)}")
        elements.append(Spacer(1, 12))
    
    # Doctor's Notes
    elements.append(Paragraph("Doctor's Notes", heading_style))
    note_text = doctor_notes or "AI-generated preliminary analysis. Please consult with a healthcare professional for clinical decision."
    elements.append(Paragraph(note_text, normal_style))
    elements.append(Spacer(1, 6))
    
    # Recommendation
    elements.append(Paragraph("Recommendation", heading_style))
    if prediction == "Pneumonia":
        recommendation = (
            "Based on the AI analysis, there are indications consistent with pneumonia. "
            "It is recommended to consult with a pulmonologist immediately. "
            "Further clinical evaluation, laboratory tests, and follow-up imaging may be necessary."
        )
    else:
        recommendation = (
            "Based on the AI analysis, the chest X-ray appears normal with no significant "
            "findings indicative of pneumonia. Regular health check-ups are advised."
        )
    elements.append(Paragraph(recommendation, normal_style))
    elements.append(Spacer(1, 20))
    
    # QR Code
    try:
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr.add_data(f"PneumoVision AI Report\nID: {pdf_filename}\nPatient: {patient_name}\nResult: {prediction}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        
        qr_table_data = [[
            Image(qr_buffer, width=0.8*inch, height=0.8*inch),
            Paragraph(
                f"<b>Verified by PneumoVision AI</b><br/>"
                f"<font size='8'>{datetime.utcnow().strftime('%Y-%m-%d')}</font>",
                ParagraphStyle("QRText", parent=normal_style, fontSize=9, alignment=TA_CENTER),
            ),
        ]]
        qr_table = Table(qr_table_data, colWidths=[1.2*inch, 2.5*inch])
        qr_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(qr_table)
    except Exception as e:
        logger.error(f"QR code generation failed: {str(e)}")
    
    elements.append(Spacer(1, 30))
    
    # Signature line
    sig_data = [[
        Paragraph(
            f"<b>{doctor_name}</b><br/>"
            f"<font size='9'>AI Diagnostic System</font><br/>"
            f"<font size='8'>PneumoVision AI • v1.0</font>",
            ParagraphStyle("Signature", parent=normal_style, fontSize=10, alignment=TA_CENTER),
        ),
    ]]
    sig_table = Table(sig_data, colWidths=[doc.width])
    sig_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
    ]))
    elements.append(sig_table)
    
    elements.append(HRFlowable(width="60%", thickness=0.5, color=GRAY_COLOR, spaceAfter=6, spaceBefore=6))
    
    # Disclaimer
    disclaimer_text = (
        "<b>Disclaimer:</b> This report is generated by an AI system and should not be used as the sole "
        "basis for clinical decision-making. The analysis is intended to assist healthcare professionals "
        "and should be interpreted in conjunction with clinical findings and professional medical judgment. "
        "This tool is not a substitute for professional medical advice, diagnosis, or treatment."
    )
    elements.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Build PDF
    doc.build(elements)
    
    logger.info(f"PDF report generated: {pdf_path}")
    return str(pdf_path)

