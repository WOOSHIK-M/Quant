import streamlit as st
from contents import pages
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")

with st.sidebar:
    selected_page = option_menu(
        menu_title="Contents",  # required
        options=[page.name for page in pages.values()],
        icons=[page.icon for page in pages.values()],
        menu_icon="cast",
        default_index=1,
    )

# display info
pages[selected_page].run()
