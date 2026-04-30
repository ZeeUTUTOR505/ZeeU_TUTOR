import streamlit as st
from services.exam_service import ExamService
from services.email_service import EmailService
from utils.common import LogSubmission, clean_student_name
import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ExamPage:

    def __init__(self, state):
        self.state = state

    def render(self):

        if st.session_state.page == "start_exam":
            self.render_start()
        else:
            self.render_exam()

    def render_start(self):

        name = st.text_input("ชื่อ")
        name = clean_student_name(name)

        test_type = st.radio(
            "ประเภท",
            ["Pre-test", "Post-test"],
            horizontal=True
        )

        exam_set = st.radio(
            "ชุดข้อสอบ",
            [1, 2, 3, 4, 5],
            horizontal=True
        )

        if st.session_state.password_type == "prelearn":
            test_type = "prelearn"
            exam_set = 1

        if st.button("เริ่ม"):
            if not name:
                st.warning("กรอกชื่อ")
            else:
                st.session_state.student_name = name
                st.session_state.test_type = test_type
                st.session_state.exam_set = exam_set
                self.state.go("exam")

    def render_exam(self):

        level = st.session_state.level
        name = st.session_state.student_name
        seed = hash(name)
        rnd = random.Random(seed)

        st.title(f"ข้อสอบ {level.upper()}")
        st.write(f"👤 {name}")

        questions, path = ExamService.load(
            level,
            st.session_state.test_type,
            st.session_state.exam_set,
            name
        )

        user_answers = []

        for i, q in enumerate(questions, 1):
            st.subheader(f"ข้อ {i}")
            st.write(q["question"])

            if q.get("image"):

                print(f"Debug: Found image for question {i}: {q['image']}")
                print(f"Debug: Checking image path: {os.path.join(BASE_DIR)}")
                print(os.getcwd())
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

            user_answers.append((q, ans))

        if st.button("ส่ง"):
            if not LogSubmission.can_submit(name, level, st.session_state.test_type):
                st.error("⛔ คุณส่งผลสอบไปแล้ว กรุณารอ 1 ชั่วโมงก่อนส่งใหม่")
                return

            score, detail = ExamService.score(user_answers)

            st.success(f"คะแนนที่ได้ {score}/{len(questions)}")

            with st.spinner("📤 กำลังส่งผลสอบ... กรุณารอสักครู่"):

                EmailService.send_exam(
                    question_path=path,
                    student_name=name,
                    level=level,
                    test_type=st.session_state.test_type,
                    score=score,
                    total=len(questions),
                    result_detail=detail
                )

                LogSubmission.save_submit_time(
                    name, level, st.session_state.test_type)

            st.success(f"✅ ผลสอบถูกส่งเข้าระบบแล้ว!")

        if st.button("⬅ กลับหน้าเลือกข้อสอบ"):
            st.session_state.page = "select_exam"
