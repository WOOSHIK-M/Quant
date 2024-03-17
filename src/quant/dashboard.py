import streamlit as st
from quant.contents import contents
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")

with st.sidebar:
    selected_content = option_menu(
        menu_title="Contents",  # required
        options=[content.name for content in contents.values()],
        icons=[content.icon for content in contents.values()],
        menu_icon="cast",
        default_index=1,
    )

# display info
contents[selected_content].run()
