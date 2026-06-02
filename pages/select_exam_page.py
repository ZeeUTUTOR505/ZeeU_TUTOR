import streamlit as st


class SelectExamPage:

    def __init__(self, state):
        self.state = state

    def render(self):

        st.title("เลือกระดับข้อสอบ")

        cols = st.columns(3)
        levels = ["m1", "m2", "m3", "m4", "m5", "m6", "pcc1", "pcc4"]

        for i, lvl in enumerate(levels):
            with cols[i % 3]:
                if st.button(f"ทำข้อสอบ {lvl.upper()}"):
                    st.session_state.level = lvl
                    self.state.go("start_exam")

        if st.button("⬅ กลับ"):
            self.state.go("home")
