import streamlit as st
from core.app_controller import AppController
from config import Config
from PIL import Image

logo = Image.open("logo.png")

st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon=logo,
    layout="wide"
)


def main():
    app = AppController()
    app.run()


if __name__ == "__main__":
    main()
