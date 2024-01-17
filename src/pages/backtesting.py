import streamlit as st

from src.pages.cache import CacheMemory


class BackTestingManager(CacheMemory):
    name = "BackTesting"
    icon = "bar-chart-line"

    @staticmethod
    def run() -> None:
        """Run a back testing page."""
        st.title("Dashboard")

        access_key = CacheMemory.get_state("access_key")
        st.write(f"access_key: {access_key}")
