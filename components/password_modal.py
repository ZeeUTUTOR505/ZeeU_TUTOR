import streamlit as st
from services.auth_service import AuthService


def render_password_modal(state):

    st.markdown("### 🔐 กรุณากรอกรหัส")

    user_input = st.text_input("รหัส", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("ยืนยัน"):
            if AuthService.validate(
                user_input,
                st.session_state.password_type
            ):
                st.session_state.ask_password = False
                state.go("select_exam")
            else:
                st.error("❌ รหัสไม่ถูกต้อง")

    with col2:
        if st.button("ยกเลิก"):
            st.session_state.ask_password = False
            st.rerun()
