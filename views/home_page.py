import streamlit.components.v1 as components
import streamlit as st
from components.password_modal import render_password_modal
from views.home import render_home, render_teachers
from utils.image_utils import get_base64
from styles.main_style import apply_style
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class HomePage:

    def __init__(self, state):
        self.state = state
        self.bg1 = get_base64("assets/hero1.jpg")
        self.bg2 = get_base64("assets/hero2.jpg")
        self.bg3 = get_base64("assets/hero3.jpg")
        self.bg4 = get_base64("assets/hero4.jpg")
        self.fb_icon = get_base64("assets/facebook.png")
        self.line_icon = get_base64("assets/line.png")
        self.phone_icon = get_base64("assets/phone.png")

    @staticmethod
    def load_style(bg1, bg2, bg3, bg4):
        css = apply_style(bg1, bg2, bg3, bg4)

        st.html(f"""
        <style>
        {css}
        </style>
        """)

    def render(self):
        HomePage.load_style(self.bg1, self.bg2, self.bg3, self.bg4)

        st.markdown("""
        <div class="announce">
            🎉 เปิดรับสมัครรอบใหม่แล้ว! รับจำนวนจำกัด
        </div>
        """, unsafe_allow_html=True)

        # Navbar
        nav1, nav2, nav3, nav4, nav5, nav6, nav7, nav8, nav9 = st.columns(
            [2.5, 1.3, 1, 1, 1, 1, 1, 1, 1]
        )
        with nav1:
            st.markdown("### ZeeU TUTOR")

        with nav2:
            if st.button("ทดสอบก่อนเรียน"):
                st.session_state.password_type = "prelearn"
                st.toast("🧠 เริ่มทำแบบทดสอบก่อนเรียน", icon="📝")
                st.session_state.ask_password = True

        with nav3:
            if st.button("ทำข้อสอบ"):
                st.session_state.password_type = "exam"
                st.session_state.ask_password = True

        with nav4:
            if st.button("สมัครเรียน"):
                self.state.go("register")

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

        with nav9:
            if st.button("🎮 เกม 24"):
                self.state.go("game")

        if st.session_state.ask_password:
            render_password_modal(self.state)

        render_home()
        render_teachers()
        self.render_announcement()

    def render_announcement(self):
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
            <img src="data:image/png;base64,{self.fb_icon}">
            <span>ZeeuTUTOR</span>
        </a>

        <a href="https://line.me/ti/g2/Xz8aX7jDsDKEsJKESX6-cCcWg8vNKrRNnLiy-g"
        target="_blank"
        class="footer-item">
            <img src="data:image/png;base64,{self.line_icon}">
            <span>OpenChat</span>
        </a>

        <a href="tel:0652941928"
        class="footer-item">
            <img src="data:image/png;base64,{self.phone_icon}">
            <span>065-294-1928</span>
        </a>

        </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
