from abc import ABCMeta

import streamlit as st
from streamlit_option_menu import option_menu


class Page(metaclass=ABCMeta):
    session_state = st.session_state

    @staticmethod
    def add_state(var, init_value=None) -> None:
        Page.session_state[var] = init_value

    @staticmethod
    def change_state(var, value):
        Page.session_state[var] = value

    @staticmethod
    def get_state(var):
        return Page.session_state[var] if var in Page.session_state else None


class HomePage(Page):

    def run(self) -> None:
        st.title("HomePage.")
        st.write(f"TEXT INPUT FROM SETTING: {Page.get_state('input')}")


class SettingPage(Page):

    def run(self) -> None:
        if Page.get_state("input") is None:
            Page.add_state("input", "Default")

        input = st.text_input("Text Input")
        if input:
            Page.change_state("input", input)
        st.write(f"INPUT: {Page.session_state.input}")


pages = {"Home": HomePage(), "Settings": SettingPage()}


with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["Home", "Settings"],
        icons=["house", "gear"],
        menu_icon="cast",
        default_index=0,
    )
pages[selected].run()
