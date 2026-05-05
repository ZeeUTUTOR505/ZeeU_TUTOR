import streamlit as st
from services.email_service import EmailService
from utils.common import Validator


class RegisterPage:

    def __init__(self, state):
        self.state = state

    def render(self):

        st.title("สมัครเรียน")

        name = st.text_input("ชื่อ-นามสกุล")
        grade = st.text_input("ระดับชั้น")
        phone = st.text_input("เบอร์ติดต่อ")

        if st.button("สมัคร"):
            if not name:
                st.warning("กรุณากรอกชื่อ")
            elif not grade:
                st.warning("กรุณากรอกระดับชั้น")
            elif not Validator.is_valid_phone(phone):
                st.warning("กรุณากรอกเบอร์ติดต่อให้ถูกต้อง")
            else:
                success = EmailService.send_register(name, grade, phone)

                if success:
                    st.success("สมัครสำเร็จ")
                else:
                    st.error("ส่งไม่สำเร็จ")

        if st.button("⬅ กลับ"):
            self.state.go("home")
