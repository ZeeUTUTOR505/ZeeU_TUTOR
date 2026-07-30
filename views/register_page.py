import streamlit as st
from services.email_service import EmailService
from utils.common import Validator


class RegisterPage:

    def __init__(self, state):
        self.state = state

    def render(self):

        st.markdown("""
        <style>

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(99,102,241,0.15), transparent 30%),
                radial-gradient(circle at bottom right, rgba(236,72,153,0.15), transparent 30%),
                linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
        }

        .block-container {
            max-width: 760px;
            padding-top: 2rem;
        }

        .input-label {
            font-weight: 700;
            margin-bottom: 8px;
            color: #0f172a;
        }

        .stTextInput input {
            border-radius: 18px !important;
            border: 2px solid transparent !important;
            padding: 15px 18px !important;
            font-size: 16px !important;

            background: rgba(255,255,255,0.9) !important;

            transition: 0.25s ease;
        }

        .stTextInput input:focus {
            border-color: #6366f1 !important;

            box-shadow:
                0 0 0 4px rgba(99,102,241,0.14) !important;
        }

        .stButton button {
            width: 100%;
            border: none;
            border-radius: 18px;
            padding: 15px;
            font-size: 17px;
            font-weight: 800;
            color: white;

            background:
                linear-gradient(
                    135deg,
                    #6366f1,
                    #8b5cf6,
                    #ec4899
                );

            transition: 0.25s ease;
        }

        .stButton button:hover {
            transform: translateY(-2px);
        }

        .stSuccess, .stWarning, .stError {
            border-radius: 16px !important;
        }

        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            text-align:center;
            padding:20px 0;
        ">
            <h1 style="
                font-size:48px;
                font-weight:900;
                margin-bottom:10px;
                background: linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899);
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;
            ">
                📚 สมัครเรียน
            </h1>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<div class="input-label" style="margin-top:30px;">👤 ชื่อ-นามสกุล</div>',
            unsafe_allow_html=True
        )

        name = st.text_input(
            "ชื่อ-นามสกุล",
            placeholder="กรอกชื่อ-นามสกุล",
            label_visibility="collapsed",
            key="register_name"
        )

        st.markdown(
            '<div class="input-label">🎓 ระดับชั้น</div>',
            unsafe_allow_html=True
        )

        grade = st.text_input(
            "ระดับชั้น",
            placeholder="เช่น ป.6 / ม.3 / ม.6",
            label_visibility="collapsed",
            key="register_grade"
        )

        st.markdown(
            '<div class="input-label">📱 เบอร์ติดต่อ</div>',
            unsafe_allow_html=True
        )

        phone = st.text_input(
            "เบอร์ติดต่อ",
            placeholder="08xxxxxxxx",
            label_visibility="collapsed",
            key="register_phone"
        )

        if st.button("✅ ยืนยันการสมัคร"):

            if not name.strip():
                st.warning("กรุณากรอกชื่อ")

            elif not grade.strip():
                st.warning("กรุณากรอกระดับชั้น")

            elif not Validator.is_valid_phone(phone):
                st.warning("กรุณากรอกเบอร์ติดต่อให้ถูกต้อง")

            else:
                with st.spinner("กำลังส่งข้อมูล..."):

                    success = EmailService.send_register(
                        name=name.strip(),
                        grade=grade.strip(),
                        phone=phone.strip()
                    )

                if success:
                    st.success(
                        "🎉 สมัครเรียนสำเร็จ ทางเราจะติดต่อกลับโดยเร็วที่สุด"
                    )
                else:
                    st.error(
                        "❌ ส่งข้อมูลไม่สำเร็จ กรุณาลองใหม่อีกครั้ง"
                    )

        if st.button("⬅ กลับ"):
            self.state.go("home")
