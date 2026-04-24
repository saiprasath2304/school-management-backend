"""
utils/pdf_generator.py
─────────────────────────────────────────────────────────────────
ReportLab-based PDF generators for:
  • Fee Receipt
  • Report Card
"""
from io import BytesIO
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


# ─── Shared helpers ───────────────────────────────────────────────────────────

def _school_header(story, styles):
    """Top section common to all PDFs: school name, address, contact."""
    school_name = getattr(settings, "SCHOOL_NAME", "Eduverse Africa")
    school_addr = getattr(settings, "SCHOOL_ADDRESS", "")
    school_ph   = getattr(settings, "SCHOOL_PHONE", "")
    school_em   = getattr(settings, "SCHOOL_EMAIL", "")

    story.append(Paragraph(school_name, styles["SchoolName"]))
    story.append(Paragraph(school_addr, styles["Normal"]))
    story.append(Paragraph(f"Tel: {school_ph}  |  Email: {school_em}", styles["Normal"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a237e")))
    story.append(Spacer(1, 0.3 * cm))


def _get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="SchoolName",
        fontSize=18, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a237e"),
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontSize=13, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#37474f"),
        spaceAfter=10, alignment=1,  # center
    ))
    styles.add(ParagraphStyle(
        name="FieldLabel",
        fontSize=9, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#546e7a"),
    ))
    styles.add(ParagraphStyle(
        name="FieldValue",
        fontSize=10, fontName="Helvetica",
    ))
    return styles


# ─── Fee Receipt PDF ──────────────────────────────────────────────────────────

def generate_fee_receipt_pdf(receipt) -> bytes:
    """
    Generate a PDF fee receipt for the given FeeReceipt instance.
    Returns raw PDF bytes.
    """
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               topMargin=1.5*cm, bottomMargin=2*cm,
                               leftMargin=2*cm, rightMargin=2*cm)
    styles = _get_styles()
    story  = []

    _school_header(story, styles)

    story.append(Paragraph("FEE RECEIPT", styles["DocTitle"]))
    story.append(Spacer(1, 0.2 * cm))

    # Receipt meta
    meta_data = [
        ["Receipt No:", receipt.receipt_number,
         "Date:", str(receipt.payment_date)],
        ["Academic Year:", str(receipt.academic_year),
         "Payment Mode:", receipt.get_payment_mode_display()],
    ]
    if receipt.reference_number:
        meta_data.append(["Reference:", receipt.reference_number, "", ""])

    meta_table = Table(meta_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    meta_table.setStyle(TableStyle([
        ("FONT",      (0, 0), (-1, -1), "Helvetica",      9),
        ("FONT",      (0, 0), (0, -1), "Helvetica-Bold",  9),
        ("FONT",      (2, 0), (2, -1), "Helvetica-Bold",  9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#546e7a")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#546e7a")),
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4 * cm))

    # Student info
    student = receipt.student
    student_data = [
        ["Student Name:", student.full_name],
        ["Admission No:", student.admission_number],
        ["Class:",        str(student.current_class) if student.current_class else "—"],
        ["Parent/Guardian:", student.parent_name or "—"],
    ]
    st_table = Table(student_data, colWidths=[4*cm, 13*cm])
    st_table.setStyle(TableStyle([
        ("FONT",      (0, 0), (0, -1), "Helvetica-Bold", 9),
        ("FONT",      (1, 0), (1, -1), "Helvetica",      10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#546e7a")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
        ("BOX",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cfd8dc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#eceff1")),
    ]))
    story.append(st_table)
    story.append(Spacer(1, 0.5 * cm))

    # Payment detail
    story.append(Paragraph("Payment Details", styles["DocTitle"]))
    payment_data = [
        ["#", "Fee Head", "Month/Period", "Amount (KES)"],
        ["1", receipt.fee_head.name, receipt.month or "—", f"{receipt.amount_paid:,.2f}"],
        ["", "", "TOTAL", f"{receipt.amount_paid:,.2f}"],
    ]
    pay_table = Table(payment_data, colWidths=[1*cm, 7*cm, 5*cm, 4*cm])
    pay_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#1a237e")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONT",          (0, 0), (-1, 0),  "Helvetica-Bold", 9),
        ("FONT",          (0, 1), (-1, -1), "Helvetica",      9),
        ("ALIGN",         (3, 0), (3, -1),  "RIGHT"),
        ("FONT",          (0, -1), (-1, -1), "Helvetica-Bold", 9),
        ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#e8eaf6")),
        ("LINEABOVE",     (0, -1), (-1, -1), 1, colors.HexColor("#1a237e")),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#cfd8dc")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.25, colors.HexColor("#eceff1")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ]))
    story.append(pay_table)
    story.append(Spacer(1, 0.8 * cm))

    # Remarks
    if receipt.remarks:
        story.append(Paragraph(f"Remarks: {receipt.remarks}", styles["Normal"]))
        story.append(Spacer(1, 0.4 * cm))

    # Collected by + footer
    story.append(Spacer(1, 1.5 * cm))
    sig_data = [
        ["_____________________", "_____________________"],
        ["Collected By",         "Parent / Guardian"],
        [receipt.collected_by.get_full_name() if receipt.collected_by else "", ""],
    ]
    sig_table = Table(sig_data, colWidths=[8.5*cm, 8.5*cm])
    sig_table.setStyle(TableStyle([
        ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
        ("FONT",   (0, 1), (-1, 1),  "Helvetica-Bold", 9),
        ("FONT",   (0, 2), (-1, 2),  "Helvetica",      8),
        ("TEXTCOLOR", (0, 1), (-1, 2), colors.HexColor("#546e7a")),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "This is a computer-generated receipt. No signature required.",
        ParagraphStyle("footer", fontSize=7, textColor=colors.grey, alignment=1)
    ))

    doc.build(story)
    return buffer.getvalue()


# ─── Report Card PDF ──────────────────────────────────────────────────────────

def generate_report_card_pdf(report_card) -> bytes:
    """
    Generate a PDF report card for the given ReportCard instance.
    Fetches all marks for student + exam, computes totals and grade.
    Returns raw PDF bytes.
    """
    from exams.models import Mark

    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               topMargin=1.5*cm, bottomMargin=2*cm,
                               leftMargin=2*cm, rightMargin=2*cm)
    styles = _get_styles()
    story  = []

    _school_header(story, styles)

    story.append(Paragraph("STUDENT REPORT CARD", styles["DocTitle"]))
    story.append(Spacer(1, 0.2 * cm))

    # Student + exam info
    student = report_card.student
    exam    = report_card.exam
    info_data = [
        ["Student:", student.full_name,    "Adm No:",    student.admission_number],
        ["Class:",   str(student.current_class) if student.current_class else "—",
         "Exam:",    str(exam)],
        ["Term:",    exam.get_term_display(), "Year:",   str(exam.academic_year)],
    ]
    info_table = Table(info_data, colWidths=[3*cm, 6.5*cm, 3*cm, 6.5*cm])
    info_table.setStyle(TableStyle([
        ("FONT",      (0, 0), (0, -1), "Helvetica-Bold", 9),
        ("FONT",      (2, 0), (2, -1), "Helvetica-Bold", 9),
        ("FONT",      (1, 0), (1, -1), "Helvetica",      10),
        ("FONT",      (3, 0), (3, -1), "Helvetica",      10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#546e7a")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#546e7a")),
        ("BACKGROUND",(0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
        ("BOX",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cfd8dc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#eceff1")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5 * cm))

    # Marks table
    marks = Mark.objects.filter(exam=exam, student=student).select_related("subject").order_by("subject__name")
    marks_data = [["#", "Subject", f"Marks / {exam.max_marks}", "Percentage", "Grade"]]
    total_marks = 0
    for i, m in enumerate(marks, start=1):
        marks_data.append([
            str(i), m.subject.name,
            str(m.marks_obtained),
            f"{m.percentage}%",
            m.grade_letter,
        ])
        total_marks += float(m.marks_obtained)

    max_total = exam.max_marks * len(marks)
    overall_pct = round(total_marks / max_total * 100, 1) if max_total else 0

    def _overall_grade(pct):
        if pct >= 80: return "A+"
        if pct >= 70: return "A"
        if pct >= 60: return "B+"
        if pct >= 50: return "B"
        if pct >= 40: return "C"
        if pct >= 33: return "D"
        return "F"

    marks_data.append(["", "TOTAL", f"{total_marks:.0f} / {max_total}", f"{overall_pct}%", _overall_grade(overall_pct)])

    col_widths = [1*cm, 7*cm, 4*cm, 4*cm, 3*cm]
    marks_table = Table(marks_data, colWidths=col_widths)
    marks_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0),  (-1, 0),  colors.HexColor("#1a237e")),
        ("TEXTCOLOR",     (0, 0),  (-1, 0),  colors.white),
        ("FONT",          (0, 0),  (-1, 0),  "Helvetica-Bold", 9),
        ("FONT",          (0, 1),  (-1, -2), "Helvetica",      9),
        ("FONT",          (0, -1), (-1, -1), "Helvetica-Bold", 9),
        ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#e8eaf6")),
        ("LINEABOVE",     (0, -1), (-1, -1), 1, colors.HexColor("#1a237e")),
        ("ALIGN",         (2, 0),  (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f9f9f9")]),
        ("BOX",           (0, 0),  (-1, -1), 0.5, colors.HexColor("#cfd8dc")),
        ("INNERGRID",     (0, 0),  (-1, -1), 0.25, colors.HexColor("#eceff1")),
        ("BOTTOMPADDING", (0, 0),  (-1, -1), 5),
        ("TOPPADDING",    (0, 0),  (-1, -1), 5),
    ]))
    story.append(marks_table)
    story.append(Spacer(1, 0.8 * cm))

    # Grading scale legend
    story.append(Paragraph("Grading Scale: A+(80+) | A(70-79) | B+(60-69) | B(50-59) | C(40-49) | D(33-39) | F(<33)",
                            ParagraphStyle("legend", fontSize=8, textColor=colors.grey)))
    story.append(Spacer(1, 1.5 * cm))

    # Signatures
    sig_data = [
        ["_________________", "_________________", "_________________"],
        ["Class Teacher",     "Principal",         "Parent / Guardian"],
    ]
    sig_table = Table(sig_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
    sig_table.setStyle(TableStyle([
        ("ALIGN",     (0, 0), (-1, -1), "CENTER"),
        ("FONT",      (0, 1), (-1, 1),  "Helvetica-Bold", 9),
        ("TEXTCOLOR", (0, 1), (-1, 1),  colors.HexColor("#546e7a")),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "This is a computer-generated report card.",
        ParagraphStyle("footer", fontSize=7, textColor=colors.grey, alignment=1)
    ))

    doc.build(story)
    return buffer.getvalue()
