
from datetime import datetime
from dotenv import load_dotenv
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

current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, ".."))
env_path = os.path.join(project_root, "secrect", ".env")
load_dotenv(env_path)


class RandomSuggestion:

    @staticmethod
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
        TTFont(
            "ThaiThin", f"{BASE_DIR}/fonts/NotoSansThai_Condensed-Thin.ttf")
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
            f"{score} / {total}", value_style)],
        [Paragraph("เปอร์เซ็นต์", label_style), Paragraph(
            f"{round(score/total*100)}%", value_style)]
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
    suggestions = RandomSuggestion.generate_suggestion(topic_stats)

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
        onPage=add_watermark
    )

    pdf.addPageTemplates([template])

    pdf.build(elements)

    return file_path


def generate_question_pdf(question_path):

    question_path = os.path.join(BASE_DIR, question_path)
    with open(question_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pdf_file = "Questions_Answer.pdf"
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4

    pdfmetrics.registerFont(TTFont(
        'THSarabunNew',
        f"{BASE_DIR}/fonts/THSarabunNew.ttf"
    ))
    left_margin = 50
    right_margin = 50
    top_margin = 50
    bottom_margin = 50

    y = height - top_margin

    def unicode_to_html_sup(text):
        SUPERSCRIPT_TO_NORMAL = str.maketrans({
            "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
            "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
            "⁺": "+", "⁻": "-", "⁽": "(", "⁾": ")"
        })

        def repl(match):
            exp = match.group(0).translate(SUPERSCRIPT_TO_NORMAL)
            return f"<sup>{exp}</sup>"

        return re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾]+", repl, text or "")

    def normalize_text(text):
        if not text:
            return ""

        text = unicode_to_html_sup(text)
        replace_map = {
            "π": "pi",
            "×": " × ",
            "÷": " ÷ ",
            "−": "-",
            "□": "A",
            "≠": "!=",
            "≤": "<=",
            "≥": ">=",
            "√": "√",
            "∛": " รากที่สามของ ",
            "∜": " รากที่สี่ของ ",
            "⁵√": " รากที่ห้าของ ",
            "⁶√": " รากที่หกของ ",
            "⁷√": " รากที่เจ็ดของ ",
            "⁸√": " รากที่แปดของ ",
            "⁹√": " รากที่เก้าของ ",
            "±": " +/- ",
            "∓": " -/+ ",
            "•": " * ",
            "·": " * ",
            "≈": " ≈ ",
            "≡": " ≡ ",
            "∝": " แปรผันตรงกับ ",
            "∈": " เป็นสมาชิกของ ",
            "∉": " ไม่เป็นสมาชิกของ ",
            "⊂": " เป็นสับเซตของ ",
            "⊄": " ไม่เป็นสับเซตของ ",
            "∪": " ยูเนียน ",
            "∩": " อินเตอร์เซกชัน ",
            "∅": "เซตว่าง",
            "∀": " สำหรับทุกตัว ",
            "∃": " มีบางตัว ",
            "∴": " ดังนั้น ",
            "∵": " เพราะว่า ",
            "∞": "อินฟินิตี้",
            "∑": "ผลรวม",
            "∏": "ผลคูณ",
            "∂": "ดิฟเฟอเรนเชียลย่อย",
            "∆": "เดลตา",
            "α": "alpha",
            "β": "beta",
            "γ": "gamma",
            "θ": "theta",
            "λ": "lambda",
            "μ": "mu",
            "σ": "sigma",
            "ω": "omega",
            "Δ": "Delta",
            "°": " องศา ",
            "∠": " มุม ",
            "⊥": " ตั้งฉากกับ ",
            "∥": " ขนานกับ ",
            "…": "...",
        }
        for k, v in replace_map.items():
            text = text.replace(k, v)

        def convert_power_to_html(match):
            exp = match.group(1).replace("(", "").replace(")", "")
            return f"<sup>{exp}</sup>"

        text = re.sub(r"\\?\^(-?\d+|\(\-?\d+\))",
                      convert_power_to_html, text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def check_page_space(required_height):
        nonlocal y
        if y - required_height < bottom_margin:
            c.showPage()
            y = height - top_margin

    def draw_multiline_text(text, font_size=16):
        nonlocal y

        max_width = width - left_margin - right_margin

        thai_paragraph_style = ParagraphStyle(
            name='ThaiParagraphStyle',
            fontName='THSarabunNew',
            fontSize=font_size,
            leading=22,
            textColor='black'
        )

        p = Paragraph(str(text), thai_paragraph_style)
        p_width, p_height = p.wrap(max_width, y)

        check_page_space(p_height)

        y -= p_height
        p.drawOn(c, left_margin, y)
        y -= 15

    def draw_solution_lines(num_lines=9):
        nonlocal y
        for _ in range(num_lines):
            check_page_space(20)
            c.line(left_margin, y, width - right_margin, y)
            y -= 20

    def estimate_text_height(text):
        wrapped = textwrap.wrap(str(text), width=90)
        return len(wrapped) * 20

    def format_choices(choices):
        if isinstance(choices, list):
            return " , ".join([f"{c}" for c in choices])
        return str(choices)

    for item in data:
        no = item["no"]

        question = normalize_text(item.get("question", ""))
        answer = normalize_text(item.get("answer", ""))
        raw_choices = item.get("choices", "")
        if isinstance(raw_choices, list):
            choices_str = format_choices(raw_choices)
        else:
            choices_str = str(raw_choices)

        choices = normalize_text(choices_str)

        q_text = f"{no}. {question}"
        c_text = f"ตัวเลือก: {format_choices(choices)}"
        a_text = f"คำตอบ: {answer}"

        # estimate space
        q_height = estimate_text_height(q_text)
        c_height = estimate_text_height(c_text)
        a_height = estimate_text_height(a_text)
        solution_height = 9 * 20 + 20

        img_height = 0
        if item.get("image"):
            try:
                img = ImageReader(f"{BASE_DIR}/{item['image']}")
                img_w, img_h = img.getSize()

                max_width = width - left_margin - right_margin
                scale = min(max_width / img_w, 0.4)

                img_height = img_h * scale + 10
            except:
                pass

        total_needed = q_height + c_height + a_height + img_height + solution_height + 40

        if y - total_needed < bottom_margin:
            c.showPage()
            y = height - top_margin

        draw_multiline_text(q_text)
        y -= 5

        if item.get("image"):
            try:
                img = ImageReader(f"{BASE_DIR}/{item['image']}")
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

        draw_multiline_text(c_text, font_size=14)
        draw_multiline_text("วิธีทำ:", font_size=16)
        draw_solution_lines(9)
        draw_multiline_text(a_text, font_size=16)
        y -= 20

    c.save()
    return pdf_file


def get_secret(key, default=None):
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)


class EmailServicec:

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_TLS_PORT = 587
    SMTP_SSL_PORT = 465

    @staticmethod
    def _get_secret(key, default=None):
        if key in st.secrets:
            return st.secrets[key]
        return os.getenv(key, default)

    @staticmethod
    def _get_credentials():
        return (
            EmailServicec._get_secret("EMAIL_USER"),
            EmailServicec._get_secret("EMAIL_PASS"),
            EmailServicec._get_secret("EMAIL_RECEIVER"),
        )

    @staticmethod
    def _normalize_receivers(receivers):
        return receivers if isinstance(receivers, list) else [receivers]

    @staticmethod
    def _attach_file(msg, file_path):
        if not os.path.exists(file_path):
            return

        with open(file_path, "rb") as f:
            part = MIMEBase("application", "pdf")
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{os.path.basename(file_path)}"',
        )
        msg.attach(part)

    @staticmethod
    def _send_smtp(sender, password, receivers, msg, use_ssl=False):
        try:
            if use_ssl:
                server = smtplib.SMTP_SSL(
                    EmailServicec.SMTP_SERVER,
                    EmailServicec.SMTP_SSL_PORT,
                    timeout=10,
                )
            else:
                server = smtplib.SMTP(
                    EmailServicec.SMTP_SERVER,
                    EmailServicec.SMTP_TLS_PORT,
                )
                server.starttls()

            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            return True

        except smtplib.SMTPAuthenticationError:
            st.error("❌ Email login failed. ตรวจสอบ App Password")
        except smtplib.SMTPException as e:
            st.error(f"❌ SMTP Error: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected Error: {e}")

        return False

    @staticmethod
    def send_exam_result_email(
        question_path,
        student_name,
        level,
        test_type,
        score,
        total,
        result_detail,
    ):
        sender, password, receivers = EmailServicec._get_credentials()
        receivers = EmailServicec._normalize_receivers(receivers)

        date = datetime.now().strftime("%Y-%m-%d")

        result_pdf = generate_exam_pdf(
            student_name, level, test_type, score, total, result_detail
        )
        question_pdf = generate_question_pdf(question_path)

        subject = f"ผลสอบ {student_name} ระดับ {level.upper()} ({test_type}) - {date}"
        body = f"""
รายงานผลการสอบ

ชื่อผู้สอบ: {student_name}
ระดับ: {level.upper()}
ประเภทการสอบ: {test_type}
คะแนน: {score} / {total}
เปอร์เซ็นต์: {round(score/total*100)}%

ไฟล์รายละเอียดผลสอบแนบมาใน PDF
"""

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = ", ".join(receivers)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # Attach files
        EmailServicec._attach_file(msg, result_pdf)
        EmailServicec._attach_file(msg, question_pdf)

        success = EmailServicec._send_smtp(
            sender, password, receivers, msg)

        # Cleanup
        for path in [result_pdf, question_pdf]:
            if path and os.path.exists(path):
                os.remove(path)

        if "chart_path" in globals() and os.path.exists(chart_path):
            os.remove(chart_path)

        return success

    @staticmethod
    def send_email(name, grade, phone):
        sender, password, receivers = EmailServicec._get_credentials()
        receivers = EmailServicec._normalize_receivers(receivers)

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
        msg["From"] = sender
        msg["To"] = ", ".join(receivers)

        return EmailServicec._send_smtp(
            sender, password, receivers, msg, use_ssl=True
        )


class Validator:

    @staticmethod
    def is_valid_phone(phone):
        digits_only = "".join(c for c in phone if c.isdigit())
        return len(digits_only) in [9, 10]


def clean_student_name(name: str) -> str:
    if not name:
        return ""
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"[^a-zA-Zก-๙\s]", "", name)
    name = name.lower()

    return name


class LogSubmission:
    @staticmethod
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

    @staticmethod
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


class PasswordGenerator:

    @staticmethod
    def generate_exam_password():
        today = datetime.now(ZoneInfo("Asia/Bangkok"))

        yy = today.year % 100
        mm = today.month
        dd = today.day

        total = (yy + mm + dd)
        password = str(total).zfill(4)[::-1] + str(dd).zfill(2)
        return password

    @staticmethod
    def generate_pretest_password():
        today = datetime.now(ZoneInfo("Asia/Bangkok"))

        yy = today.year % 100
        mm = today.month
        dd = today.day

        password = f"{str(dd).zfill(2)}{str(mm).zfill(2)}{str(yy).zfill(2)}"
        return password
