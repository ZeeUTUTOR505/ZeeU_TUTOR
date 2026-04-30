import streamlit as st
from services.email_service import EmailService
from utils.common import is_valid_phone


class RegisterPage:

    def __init__(self, state):
        self.state = state

    def render(self):

        st.title("สมัครเรียน")

        name = st.text_input("ชื่อ")
        grade = st.text_input("ระดับ")
        phone = st.text_input("เบอร์")

        if st.button("สมัคร"):
            if not name:
                st.warning("กรอกชื่อ")
            elif not grade:
                st.warning("กรอกระดับ")
            elif not is_valid_phone(phone):
                st.warning("เบอร์ไม่ถูกต้อง")
            else:
                success = EmailService.send_register(name, grade, phone)

                if success:
                    st.success("สมัครสำเร็จ")
                else:
                    st.error("ส่งไม่สำเร็จ")

        if st.button("⬅ กลับ"):
            self.state.go("home")
