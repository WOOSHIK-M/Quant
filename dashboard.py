import streamlit as st
from streamlit_option_menu import option_menu

from src.pages import pages
from src.pages.cache import CacheMemory

with st.sidebar:
    selected_page = option_menu(
        menu_title="Contents",  # required
        options=[page.name for page in pages.values()],
        icons=[page.icon for page in pages.values()],
        menu_icon="cast",
        default_index=0,
    )

# display info
pages[selected_page].run()
