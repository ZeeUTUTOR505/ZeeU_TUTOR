import streamlit as st
from core.state_manager import StateManager

from pages.home_page import HomePage
from pages.select_exam_page import SelectExamPage
from pages.exam_page import ExamPage
from pages.register_page import RegisterPage
from pages.game_page import GamePage


class AppController:

    def __init__(self):
        self.state = StateManager()

    def run(self):
        self.state.init()

        page = st.session_state.page

        if page == "home":
            HomePage(self.state).render()

        elif page == "select_exam":
            SelectExamPage(self.state).render()

        elif page in ["start_exam", "exam"]:
            ExamPage(self.state).render()

        elif page == "register":
            RegisterPage(self.state).render()

        elif page == "game":
            GamePage(self.state).render()
