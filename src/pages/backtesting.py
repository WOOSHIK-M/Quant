import json

import requests
import streamlit as st

import src.utils as utils
from src.pages.cache import CacheMemory
from src.structure import Market

UPBIT_OPEN_API_MARKET_URL = "https://api.upbit.com/v1/market"


class BackTestingManager(CacheMemory):
    """A manager to back-test."""

    name = "BackTesting"
    icon = "bar-chart-line"

    # keys for shared memory
    DICT_MARKET_INDEX = "d_market_index"
    SELECTED_MARKET = "selected_market"

    @property
    def selected_market(self) -> str:
        """Get the current selected market."""
        return CacheMemory.get_state(self.SELECTED_MARKET)

    @property
    def selected_market_index(self) -> int:
        """Get the index of selected market in the selectbox."""
        return self.d_market_index[self.selected_market]

    def run(self) -> None:
        """Run a back-testing page."""
        self.init_page()

    def init_page(self) -> None:
        """Initialize a page."""
        CacheMemory.add_state(self.SELECTED_MARKET)

        st.title("Dashboard")

        # make a select box
        market_infos = self.get_market_infos()

        self.d_market_index = {
            market: index for index, market in enumerate(market_infos)
        }
        selected_market = st.selectbox(
            label="Select a coin",
            options=list(market_infos.keys()),
            index=self.selected_market_index
            if CacheMemory.get_state(self.SELECTED_MARKET)
            else 0,
        )
        CacheMemory.change_state(self.SELECTED_MARKET, selected_market)

        # test !
        st.write(self.selected_market)

    def get_market_infos(self) -> dict[str, Market]:
        """Get all markets from Upbit."""
        _, market_info = utils.request_info(url=UPBIT_OPEN_API_MARKET_URL + "/all")

        markets = [Market(**info) for info in market_info]
        markets = {market.key: market for market in markets}
        return markets
