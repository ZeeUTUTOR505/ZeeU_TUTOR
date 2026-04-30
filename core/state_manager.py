import streamlit as st


class StateManager:

    DEFAULTS = {
        "page": "home",
        "ask_password": False,
        "student_name": "",
        "level": "",
        "test_type": "",
        "exam_set": 1,
        "password_type": None,
    }

    def init(self):
        for k, v in self.DEFAULTS.items():
            if k not in st.session_state:
                st.session_state[k] = v

    def go(self, page: str):
        st.session_state.page = page
        st.rerun()

    def reset_exam(self):
        for key in ["student_name", "level"]:
            st.session_state.pop(key, None)
