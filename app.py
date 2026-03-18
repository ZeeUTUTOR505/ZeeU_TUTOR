import os
from PIL import Image
import streamlit as st
from utils.image_utils import get_base64
from utils.question_loader import load_questions
from utils.common import generate_password, send_email, is_valid_phone, send_exam_result_email, can_submit, save_submit_time, clean_student_name
from styles.main_style import apply_style
from pages.home import render_home, render_teachers
import os

logo = Image.open("logo.png")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
st.set_page_config(
    page_title="ZeeU TUTOR",
    page_icon=logo,
    layout="wide"
)

st.set_page_config(page_title="ZeeU TUTOR", layout="wide")
# Load images
bg1 = get_base64("assets/hero1.jpg")
bg2 = get_base64("assets/hero2.jpg")
bg3 = get_base64("assets/hero3.jpg")
bg4 = get_base64("assets/hero4.jpg")
fb_icon = get_base64("assets/facebook.png")
line_icon = get_base64("assets/line.png")
phone_icon = get_base64("assets/phone.png")

# Apply style
st.markdown(apply_style(bg1, bg2, bg3, bg4), unsafe_allow_html=True)

# Page routing
if "page" not in st.session_state:
    st.session_state.page = "home"


if "ask_password" not in st.session_state:
    st.session_state.ask_password = False


if st.session_state.page == "home":
    # Announcement Bar
    st.markdown("""
    <div class="announce">
        🎉 เปิดรับสมัครรอบใหม่แล้ว! รับจำนวนจำกัด
    </div>
    """, unsafe_allow_html=True)

    # Navbar
    nav1, nav2, nav3, nav4, nav5, nav6, nav7, nav8 = st.columns(
        [2.5, 1.3, 1, 1, 1, 1, 1, 1]
    )
    with nav1:
        st.markdown("### ZeeU TUTOR")

    with nav2:
        if st.button("ทดสอบก่อนสมัคร"):
            st.toast("🧠 เริ่มทำแบบทดสอบก่อนเรียน", icon="📝")
            # st.session_state.page = "pretest"
            # st.rerun()

    with nav3:
        if st.button("ทำข้อสอบ"):
            st.session_state.ask_password = True

    with nav4:
        if st.button("สมัครเรียน"):
            st.session_state.page = "register"
            st.rerun()

    with nav5:
        if st.button("📞 ติดต่อ"):
            st.toast("📱 ติดต่อ: 065-294-1928", icon="📞")

    with nav6:
        if st.button("📚 คอร์สเรียน"):
            st.toast("🎯 คอร์สเรียนคณิตศาสตร์ ระดับชั้น มัธยม", icon="📚")

    with nav7:
        if st.button("🎉 โปรโมชัน"):
            st.toast("🔥 สมัคร 2 คนขึ้นไป ลด 10%!", icon="🎉")

    with nav8:
        if st.button("🧪 ทดลองเรียน"):
            st.toast("✨ ทดลองเรียนและทดสอบความรู้ฟรีก่อนตัดสินใจ", icon="✨")

    if st.session_state.ask_password:
        st.markdown('<div class="dimmed">', unsafe_allow_html=True)

    if st.session_state.ask_password:
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="password-wrapper">', unsafe_allow_html=True)

        st.markdown(
            '<div class="password-title">🔐 กรุณากรอกรหัสก่อนเข้าใช้งาน</div>',
            unsafe_allow_html=True
        )

        user_input = st.text_input(
            "รหัสยืนยัน",
            type="password",
            label_visibility="collapsed"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("ยืนยัน", use_container_width=True):
                if user_input == generate_password():
                    st.session_state.ask_password = False
                    st.session_state.page = "select_exam"
                    st.rerun()
                else:
                    st.error("❌ รหัสไม่ถูกต้อง")

        with col2:
            if st.button("ยกเลิก", use_container_width=True):
                st.session_state.ask_password = False
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    render_home()

    st.write("")
    render_teachers()
    st.write("")

    col1, col2 = st.columns(2)
    st.markdown(f"""
    <div class="footer">
    <div class="footer-content">
    <div class="footer-title">
    ZeeU TUTOR | ติดต่อเรา
    </div>

    <div class="footer-links">

    <a href="https://www.facebook.com/profile.php?id=61586686648790"
    target="_blank"
    class="footer-item">
        <img src="data:image/png;base64,{fb_icon}">
        <span>ZeeuTUTOR</span>
    </a>

    <a href="https://line.me/ti/g2/Xz8aX7jDsDKEsJKESX6-cCcWg8vNKrRNnLiy-g"
    target="_blank"
    class="footer-item">
        <img src="data:image/png;base64,{line_icon}">
        <span>OpenChat</span>
    </a>

    <a href="tel:0652941928"
    class="footer-item">
        <img src="data:image/png;base64,{phone_icon}">
        <span>065-294-1928</span>
    </a>

    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ================== SELECT EXAM ==================
elif st.session_state.page == "select_exam":

    st.title("เลือกระดับข้อสอบ")

    # ===== สร้าง 3 คอลัมน์ =====
    col1, col2, col3 = st.columns(3)

    # ===== ROW 1 =====
    with col1:
        if st.button("🎯 ทำข้อสอบ ม.1"):
            st.session_state.level = "m1"
            st.session_state.page = "start_exam"
    with col2:
        if st.button("📘 ทำข้อสอบ ม.2"):
            st.warning("🚧 ระดับ ม.2 กำลังพัฒนา")

    with col3:
        if st.button("📗 ทำข้อสอบ ม.3"):
            st.warning("🚧 ระดับ ม.3 กำลังพัฒนา")
    # ===== ROW 2 =====
    col4, col5, col6 = st.columns(3)

    with col4:
        if st.button("🚀 ทำข้อสอบ ม.4"):
            st.session_state.level = "m4"
            st.session_state.page = "start_exam"

    with col5:
        if st.button("📙 ทำข้อสอบ ม.5"):
            st.warning("🚧 ระดับ ม.5 กำลังพัฒนา")

    with col6:
        if st.button("🎓 ทำข้อสอบ ม.6"):
            st.warning("🚧 ระดับ ม.6 กำลังพัฒนา")

    # ===== ปุ่มกลับ =====
    if st.button("⬅ กลับหน้าแรก"):
        for key in ["student_name", "level"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.page = "home"
        st.rerun()


elif st.session_state.page == "start_exam":

    st.title("เริ่มทำข้อสอบ")
    st.subheader(f"ระดับ {st.session_state.level.upper()}")

    student_name = st.text_input("กรอกชื่อ-นามสกุล ก่อนเริ่มสอบ")
    student_name = clean_student_name(student_name)
    test_type = st.radio(
        "เลือกประเภทการสอบ",
        ["Pre-test", "Post-test"],
        horizontal=True
    )

    exam_set = st.radio(
        "เลือกชุดข้อสอบ",
        [1, 2, 3],
        horizontal=True
    )

    if st.button("เริ่มทำข้อสอบ"):
        if not student_name:
            st.warning("กรุณากรอกชื่อก่อนเริ่มสอบ")
        else:
            st.session_state.student_name = student_name
            st.session_state.test_type = test_type
            st.session_state.exam_set = exam_set
            st.session_state.page = "exam"
            st.rerun()

# ================== EXAM PAGE ==================
elif st.session_state.page == "exam":

    st.title(f"ข้อสอบระดับ {st.session_state.level.upper()}")
    st.write(f"👤 ผู้สอบ: {st.session_state.student_name}")

    if st.session_state.test_type == "Pre-test":
        question_path = f"questions/{st.session_state.level}_pretest_{st.session_state.exam_set}.json"
    else:
        question_path = f"questions/{st.session_state.level}_posttest_{st.session_state.exam_set}.json"

    import random

    questions = load_questions(question_path)
    seed = hash(st.session_state.student_name)
    rnd = random.Random(seed)

    questions = questions.copy()
    rnd.shuffle(questions)
    len_questions = len(questions)
    score = 0
    user_answers = []

    for i, q in enumerate(questions, start=1):

        st.markdown('<div class="exam-box">', unsafe_allow_html=True)

        st.subheader(f"ข้อที่ {i}")
        st.write(q["question"])

        if q.get("image"):
            image_path = os.path.join(BASE_DIR, q["image"])
            if os.path.exists(image_path):
                st.image(image_path, width=300)

        if q["choices"]:
            choices = q["choices"].copy()
            rnd.shuffle(choices)

            ans = st.radio(
                "เลือกคำตอบ",
                choices,
                key=f"q_{i}",
                index=None
            )

        elif q["choices"] is None:
            ans = st.text_input(
                "คำตอบ",
                key=f"q_{i}"
            )

        else:
            ans = ""

        user_answers.append((q, str(ans)))

        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("ส่งคำตอบ"):
        if not can_submit(
            st.session_state.student_name,
            st.session_state.level,
            st.session_state.test_type
        ):
            st.error("⛔ คุณส่งผลสอบไปแล้ว กรุณารอ 1 ชั่วโมงก่อนส่งใหม่")
            st.stop()

        score = 0
        result_detail = []

        for q, ans in user_answers:

            correct_answer = str(q["answer"]).strip()
            user_answer = str(ans).strip() if ans else ""

            is_correct = user_answer == correct_answer

            if is_correct:
                score += 1

            result_detail.append({
                "no": q["no"],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "topic": q.get("topic", "N/A"),
                "result": "ถูก" if is_correct else "ผิด"
            })

        st.success(f"✅ ส่งคำตอบสำเร็จ! ได้คะแนน {score} / {len_questions}")

        with st.spinner("📤 กำลังส่งผลสอบ... กรุณารอสักครู่"):
            send_exam_result_email(question_path=question_path,
                                   student_name=st.session_state.student_name,
                                   level=st.session_state.level,
                                   test_type=st.session_state.test_type,
                                   score=score,
                                   total=len_questions,
                                   result_detail=result_detail)

            save_submit_time(
                st.session_state.student_name,
                st.session_state.level,
                st.session_state.test_type)

        st.success(f"✅ ผลสอบถูกส่งเข้าระบบแล้ว!")

    if st.button("⬅ กลับหน้าเลือกข้อสอบ"):
        st.session_state.page = "select_exam"

# ================== REGISTER ==================
elif st.session_state.page == "register":

    st.title("สมัครเรียน")

    name = st.text_input("ชื่อ-นามสกุล")
    grade = st.text_input("ระดับชั้น")
    phone = st.text_input("เบอร์โทรศัพท์")

    if st.button("ยืนยันสมัคร"):
        if not name.strip():
            st.warning("กรุณากรอกชื่อ-นามสกุล")

        elif not grade.strip():
            st.warning("กรุณากรอกระดับชั้น")

        elif not is_valid_phone(phone):
            st.warning("กรุณากรอกเบอร์โทรศัพท์ที่ถูกต้อง (9-10 หลัก)")

        else:
            with st.spinner("⏳ กำลังตรวจสอบข้อมูล กรุณารอสักครู่..."):
                success = send_email(name, grade, phone)

            if success:
                st.success(f"ขอบคุณ คุณ {name} ทางเราจะติดต่อกลับเร็วที่สุด")
            else:
                st.warning(
                    "⚠️ ไม่สามารถส่งข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้งภายหลัง")

    if st.button("⬅ กลับหน้าแรก"):
        st.session_state.page = "home"
