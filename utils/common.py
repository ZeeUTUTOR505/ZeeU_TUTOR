
import random
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
from collections import defaultdict
from email import encoders
from email.mime.base import MIMEBase
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import json
import os
import numpy as np
from datetime import datetime, timedelta
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
import re
from reportlab.platypus import Image
import matplotlib.font_manager as fm
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import textwrap


def add_watermark(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(Color(0.9, 0.9, 0.9))
    canvas.setFont("Helvetica-Bold", 10)

    xs = [width*0.02, width*0.5, width*0.98]
    ys = [height*0.15, height*0.5]

    for x in xs:
        for y in ys:
            canvas.saveState()
            canvas.translate(x, y)
            canvas.rotate(30)
            canvas.drawCentredString(0, 0, "ZeeUTUTOR")
            canvas.restoreState()

    canvas.setFont("Helvetica-Bold", 18)
    canvas.drawCentredString(width/2, 50, "ZeeUTUTOR")
    canvas.setFont("Helvetica", 12)
    canvas.drawCentredString(width/2, 35, "Math Diagnostic Report")

    canvas.restoreState()


chart_path = "topic_chart.png"
SUBMIT_LOG_FILE = "submit_log.json"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_suggestion(topic_stats):

    good_suggestions = [
        "ทำได้ดี ควรรักษาระดับและลองทำโจทย์ที่ยากขึ้น",
        "มีความเข้าใจดี ลองฝึกโจทย์ประยุกต์เพิ่มเติม",
        "พื้นฐานแข็งแรง ควรลองโจทย์ที่ท้าทายขึ้น",
        "ทำได้ดีมาก ควรฝึกโจทย์หลากหลายรูปแบบ",
        "มีความเข้าใจดี ลองทำข้อสอบแข่งขันหรือโจทย์ยากขึ้น"
    ]

    mid_suggestions = [
        "ควรฝึกทำโจทย์เพิ่มเติมเพื่อเพิ่มความแม่นยำ",
        "ควรทบทวนแนวคิดหลักและฝึกโจทย์ประยุกต์",
        "ยังสามารถพัฒนาได้ ลองฝึกโจทย์หลากหลายรูปแบบ",
        "ควรฝึกทำแบบฝึกหัดเพิ่มเติมเพื่อให้เข้าใจมากขึ้น",
        "ลองทบทวนบทเรียนและทำโจทย์เพิ่มเพื่อเพิ่มความมั่นใจ"
    ]

    low_suggestions = [
        "ควรทบทวนพื้นฐานของหัวข้อนี้ก่อน",
        "ควรกลับไปฝึกโจทย์พื้นฐานเพิ่มเติม",
        "แนะนำให้ทบทวนแนวคิดหลักของบทเรียน",
        "ควรเริ่มจากแบบฝึกหัดระดับง่ายก่อน",
        "ควรฝึกทำโจทย์พื้นฐานเพื่อสร้างความเข้าใจ"
    ]

    suggestions = []

    for topic, data in topic_stats.items():

        p = data["percent"]

        if p >= 80:
            suggestion = random.choice(good_suggestions)

        elif p >= 50:
            suggestion = random.choice(mid_suggestions)

        else:
            suggestion = random.choice(low_suggestions)

        suggestions.append(f"หัวข้อ {topic} {suggestion}")

    return suggestions


def create_topic_chart(topic_stats):

    font_path = "fonts/NotoSansThai_Condensed-Black.ttf"
    font_prop = fm.FontProperties(fname=font_path)

    topics = list(topic_stats.keys())

    scores = [topic_stats[t]["correct"] for t in topics]
    totals = [topic_stats[t]["total"] for t in topics]

    # เปลี่ยนเป็น percent
    percents = [(s/t)*100 for s, t in zip(scores, totals)]

    N = len(topics)

    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()

    # ปิดวง
    percents += percents[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(subplot_kw=dict(polar=True))

    ax.plot(angles, percents, linewidth=2)
    ax.fill(angles, percents, alpha=0.25)

    ax.set_ylim(0, 100)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(topics, fontproperties=font_prop)
    chart_path = "topic_chart.png"

    plt.savefig(chart_path, bbox_inches="tight")
    plt.close()

    return chart_path


def summarize_by_topic(result_detail):

    topic_stats = defaultdict(lambda: {"correct": 0, "total": 0})

    for item in result_detail:
        topic = item["topic"]

        topic_stats[topic]["total"] += 1

        if item["result"] == "ถูก":
            topic_stats[topic]["correct"] += 1

    for topic in topic_stats:
        c = topic_stats[topic]["correct"]
        t = topic_stats[topic]["total"]
        topic_stats[topic]["percent"] = round((c/t)*100)

    return topic_stats


def generate_exam_pdf(student_name, level, test_type, score, total, result_detail):

    file_path = f"Exam-Result-{test_type.replace('_', '-')}.pdf"

    # register font
    pdfmetrics.registerFont(
        TTFont(
            "ThaiFont", f"{BASE_DIR}/fonts/NotoSansThai_Condensed-Medium.ttf")
    )

    pdfmetrics.registerFont(
        TTFont("ThaiRegular",
               f"{BASE_DIR}/fonts/NotoSansThai_Condensed-Regular.ttf")
    )

    pdfmetrics.registerFont(
        TTFont("ThaiThin", f"{BASE_DIR}/fonts/NotoSansThai_Condensed-Thin.ttf")
    )

    label_style = ParagraphStyle(
        "Label",
        fontName="ThaiRegular",
        fontSize=12
    )

    value_style = ParagraphStyle(
        "Value",
        fontName="ThaiThin",
        fontSize=12
    )

    data_info = [
        [Paragraph("ชื่อผู้สอบ", label_style),
         Paragraph(student_name, value_style)],
        [Paragraph("ระดับ", label_style), Paragraph(
            level.upper(), value_style)],
        [Paragraph("ประเภทการสอบ", label_style),
         Paragraph(test_type, value_style)],
        [Paragraph("คะแนน", label_style), Paragraph(
            f"{score} / {total}", value_style)]
    ]
    info_table = Table(data_info, colWidths=[100, 300])

    # styles
    title_style = ParagraphStyle(
        "Title",
        fontName="ThaiFont",
        fontSize=24,
        alignment=1
    )

    sub_title_style = ParagraphStyle(
        "SubTitle",
        fontName="ThaiFont",
        fontSize=18,
        alignment=1)

    title = Paragraph(
        "รายงานผลการสอบ",
        title_style
    )

    data = [["หัวข้อ", "ทำถูก", "จำนวนข้อ", "เปอร์เซ็นต์"]]
    topic_stats = summarize_by_topic(result_detail)
    for topic, stat in topic_stats.items():

        correct = stat["correct"]
        total = stat["total"]

        percent = round(correct/total*100)

        data.append([
            topic,
            correct,
            total,
            f"{percent}%"
        ])

    table = Table(data, colWidths=[5*cm, 3*cm, 3*cm, 3*cm])

    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "ThaiFont"),

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 1, colors.grey),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke)
    ]))

    sub_title_charts = Paragraph(
        "วิเคราะห์คะแนนแต่ละหัวข้อ",
        sub_title_style
    )

    chart_path = create_topic_chart(topic_stats)
    chart = Image(chart_path, width=360, height=225)
    suggestions = generate_suggestion(topic_stats)

    # elements.append(Spacer(1, 20))
    advice = Paragraph("คำแนะนำ", sub_title_style)

    suggest = []
    for s in suggestions:
        suggest.append(Paragraph(f"• {s}", value_style))

    space = Spacer(1, 20)
    elements = [
        space,
        title,
        space, space,
        info_table,
        space,
        table,
        space,
        sub_title_charts,
        space, space,
        chart,
        space,
        advice,
        space,
        *suggest

    ]

    frame = Frame(
        40,
        40,
        A4[0] - 80,
        A4[1] - 80,
        id="normal"
    )

    pdf = BaseDocTemplate(
        file_path,
        pagesize=A4
    )

    template = PageTemplate(
        id="test",
        frames=frame,
        # onPageEnd=add_watermark
        onPage=add_watermark
    )

    pdf.addPageTemplates([template])

    pdf.build(elements)

    return file_path


def generate_password():
    today = datetime.now(ZoneInfo("Asia/Bangkok"))

    yy = today.year % 100
    mm = today.month
    dd = today.day

    total = (yy + mm + dd)
    password = str(total).zfill(4)[::-1] + str(dd).zfill(2)
    return password


def generate_question_pdf(question_path):

    question_path = os.path.join(BASE_DIR, question_path)
    with open(question_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pdf_file = "Questions_Answer.pdf"
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4

    # Font
    pdfmetrics.registerFont(TTFont(
        'THSarabun',
        f"{BASE_DIR}/fonts/THSarabunNew.ttf"
    ))
    c.setFont('THSarabun', 16)

    # Layout
    left_margin = 50
    right_margin = 50
    top_margin = 50
    bottom_margin = 50

    y = height - top_margin

    def check_page_space(required_height):
        nonlocal y
        if y - required_height < bottom_margin:
            c.showPage()
            c.setFont('THSarabun', 16)
            y = height - top_margin

    def normalize_text(text):
        return text.replace("π", "pi")

    def draw_multiline_text(text):
        nonlocal y
        wrapped = textwrap.wrap(text, width=90)
        for line in wrapped:
            check_page_space(20)
            c.drawString(left_margin, y, line)
            y -= 20

    def draw_solution_lines(num_lines=5):
        nonlocal y
        for _ in range(num_lines):
            check_page_space(20)
            c.line(left_margin, y, width - right_margin, y)
            y -= 20

    def estimate_text_height(text):
        wrapped = textwrap.wrap(text, width=90)
        return len(wrapped) * 20

    for item in data:
        no = item["no"]
        question = normalize_text(item["question"])
        answer = item["answer"]

        # Estimate space
        q_height = estimate_text_height(f"{no}. {question}")
        a_height = estimate_text_height(f"คำตอบ: {answer}")
        solution_height = 5 * 20 + 20

        img_height = 0
        if "image" in item and item["image"]:
            try:
                img = ImageReader(f"{BASE_DIR}/{item['image']}")
                img_w, img_h = img.getSize()

                max_width = width - left_margin - right_margin
                scale = min(max_width / img_w, 0.4)
                img_height = img_h * scale + 10
            except:
                pass

        total_needed = q_height + img_height + solution_height + a_height + 40

        if y - total_needed < bottom_margin:
            c.showPage()
            c.setFont('THSarabun', 16)
            y = height - top_margin

        draw_multiline_text(f"{no}. {question}")
        y -= 5

        # Image
        if "image" in item and item["image"]:
            try:
                img = ImageReader("../" + item["image"])
                img_w, img_h = img.getSize()

                max_width = width - left_margin - right_margin
                scale = min(max_width / img_w, 0.4)
                img_w *= scale
                img_h *= scale

                check_page_space(img_h + 10)
                c.drawImage(img, left_margin, y - img_h,
                            width=img_w, height=img_h)
                y -= img_h + 10
            except:
                pass

        # Solution
        draw_multiline_text("วิธีทำ:")
        draw_solution_lines(5)

        # Answer
        draw_multiline_text(f"คำตอบ: {answer}")
        y -= 20

    # Save
    c.save()

    return pdf_file


def send_exam_result_email(question_path, student_name, level, test_type, score, total, result_detail):

    sender_email = st.secrets["EMAIL_USER"]
    sender_password = st.secrets["EMAIL_PASS"]
    receiver_email = st.secrets["EMAIL_USER"]
    date = datetime.now().strftime("%Y-%m-%d")
    result_pdf_path = generate_exam_pdf(
        student_name,
        level,
        test_type,
        score,
        total,
        result_detail
    )
    pdf_question_path = generate_question_pdf(question_path)

    subject = f"ผลสอบ {student_name} ระดับ {level.upper()} ({test_type}) - {date}"

    body = f"""
    รายงานผลการสอบ

    ชื่อผู้สอบ: {student_name}
    ระดับ: {level.upper()}
    ประเภทการสอบ: {test_type}
    คะแนน: {score} / {total}

    ไฟล์รายละเอียดผลสอบแนบมาใน PDF
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    # Attach result PDF
    with open(result_pdf_path, "rb") as f:
        part1 = MIMEBase("application", "pdf")
        part1.set_payload(f.read())

    encoders.encode_base64(part1)

    part1.add_header(
        "Content-Disposition",
        f'attachment; filename="{os.path.basename(result_pdf_path)}"'
    )

    msg.attach(part1)

    # Attach question PDF
    with open(pdf_question_path, "rb") as f:
        part2 = MIMEBase("application", "pdf")
        part2.set_payload(f.read())

    encoders.encode_base64(part2)

    part2.add_header(
        "Content-Disposition",
        f'attachment; filename="{os.path.basename(pdf_question_path)}"'
    )

    msg.attach(part2)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการส่งอีเมล: {e}")
        return False

    finally:
        for path in [result_pdf_path, pdf_question_path]:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(chart_path):
            os.remove(chart_path)


def send_email(name, grade, phone):
    try:
        # --------- Load Secrets ----------
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASS"]
        receiver_emails = st.secrets["EMAIL_RECEIVER"]

        if isinstance(receiver_emails, str):
            receiver_emails = [receiver_emails]

        # --------- Email Content ----------
        subject = "มีผู้สมัครเรียนใหม่ - ZeeU TUTOR"
        body = f"""
        ========================================
                📌 แจ้งเตือนผู้สมัครเรียนใหม่
        ========================================

        👤 ชื่อ-นามสกุล : {name}
        🎓 ระดับชั้น     : {grade}
        📞 เบอร์โทรศัพท์ : {phone}

        ----------------------------------------
        กรุณาติดต่อกลับโดยเร็วที่สุด
        ========================================
        """

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = ", ".join(receiver_emails)

        # --------- Send Email ----------
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(sender_email, sender_password)
            server.sendmail(
                sender_email,
                receiver_emails,
                msg.as_string()
            )

        return True

    except KeyError as e:
        st.error(f"❌ Missing secret key: {e}")
        return False

    except smtplib.SMTPAuthenticationError:
        st.error("❌ Email login failed. ตรวจสอบ App Password")
        return False

    except smtplib.SMTPException as e:
        st.error(f"❌ SMTP Error: {e}")
        return False

    except Exception as e:
        st.error(f"❌ Unexpected Error: {e}")
        return False


def is_valid_phone(phone):
    digits_only = "".join(c for c in phone if c.isdigit())
    if len(digits_only) in [9, 10]:
        return True
    return False


def clean_student_name(name: str) -> str:
    if not name:
        return ""
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"[^a-zA-Zก-๙\s]", "", name)
    name = name.lower()

    return name


def can_submit(student_name, level, test_type):

    key = f"{student_name}_{level}_{test_type}"

    if not os.path.exists(SUBMIT_LOG_FILE):
        return True

    with open(SUBMIT_LOG_FILE, "r") as f:
        data = json.load(f)

    if key not in data:
        return True

    last_submit_time = datetime.fromisoformat(data[key])
    if datetime.now() - last_submit_time < timedelta(hours=1):
        return False

    return True


def save_submit_time(student_name, level, test_type):

    key = f"{student_name}_{level}_{test_type}"

    if os.path.exists(SUBMIT_LOG_FILE):
        with open(SUBMIT_LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[key] = datetime.now().isoformat()

    with open(SUBMIT_LOG_FILE, "w") as f:
        json.dump(data, f)
