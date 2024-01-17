from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

import src.utils as utils
from src.pages.cache import CacheMemory

UPBIT_OPEN_API_ACCOUNT_URL = "https://api.upbit.com/v1/accounts"


class LoginManager(CacheMemory):
    """Connect to Upbit account.

    Reference:
        https://docs.upbit.com/docs/create-authorization-request
    """

    name = "Home"
    icon = "house"

    # keys for share memory
    ACCESS_KEY = "access_key"
    SECRET_KEY = "secret_key"
    ACCOUNT_INFO = "account_info"

    IS_LOGGED_IN = "is_logged_in"

    @property
    def access_key(self) -> str:
        """Get access key from the shared memory."""
        return CacheMemory.get_state(self.ACCESS_KEY)

    @property
    def secret_key(self) -> str:
        """Get secret key from the shared memory."""
        return CacheMemory.get_state(self.SECRET_KEY)

    @property
    def account_info(self) -> dict[str, Any]:
        """Get account info from the shared memory."""
        return CacheMemory.get_state(self.ACCOUNT_INFO)

    @property
    def is_logged_in(self) -> bool:
        """Get account info from the shared memory."""
        return CacheMemory.get_state(self.IS_LOGGED_IN)

    def run(self) -> None:
        """Run a login page."""
        self._init_page()

        # do log in
        if not self.is_logged_in and self.log_in_button.button("Log in"):
            self.log_in()

        # do log out
        if self.is_logged_in and self.log_in_button.button("Log out"):
            self.log_out()

        # display account info if logged-in
        self.display_account_info()

    def _init_page(self) -> None:
        """Initialize a page."""
        CacheMemory.add_state(self.ACCESS_KEY, value="")
        CacheMemory.add_state(self.SECRET_KEY, value="")
        CacheMemory.add_state(self.ACCOUNT_INFO, value=None)
        CacheMemory.add_state(self.IS_LOGGED_IN, value=False)

        st.title("Upbit Account")

        # make two text boxed to get keys to access the account
        self.text_access_key = st.text_input(label="Access Key")
        self.text_secret_key = st.text_input(label="Secret Key", type="password")

        # log-in & log-out button
        self.log_in_button = st.empty()

    def log_in(self) -> None:
        """Log in and save account info to shared memory."""
        success_to_login, account_info = utils.get_account_info(
            url=UPBIT_OPEN_API_ACCOUNT_URL,
            access_key=self.text_access_key,
            secret_key=self.text_secret_key,
        )
        CacheMemory.change_state(self.ACCESS_KEY, self.text_access_key)
        CacheMemory.change_state(self.SECRET_KEY, self.text_secret_key)
        CacheMemory.change_state(self.IS_LOGGED_IN, success_to_login)
        CacheMemory.change_state(self.ACCOUNT_INFO, account_info)

        # check if logged in normally
        if not success_to_login:
            self.display_incorrect_login()

    def log_out(self) -> None:
        """Log out and delete account info."""
        CacheMemory.change_state(self.ACCESS_KEY, "")
        CacheMemory.change_state(self.SECRET_KEY, "")
        CacheMemory.change_state(self.ACCOUNT_INFO, None)
        CacheMemory.change_state(self.IS_LOGGED_IN, False)

        self.log_in_button.button("Log in")

    def display_account_info(self) -> None:
        """Display the current account information."""
        if not self.account_info:
            return

        st.subheader("Account INFO.")
        df = pd.DataFrame(self.account_info)

        # TODO: only display unit_currency == KRW
        st.text("NOTE: Only display `KRW` coins currently.")
        df = df[df["unit_currency"] == "KRW"]

        df["balance"] = df["balance"].astype(float)
        df["avg_buy_price"] = df["avg_buy_price"].astype(float)
        df["overall_price"] = df["balance"] * df["avg_buy_price"]
        fig = px.pie(df, values="overall_price", names="currency", hole=0.3)

        # display information
        st.plotly_chart(fig)

    def display_incorrect_login(self) -> None:
        """Display a login failure."""
        st.text(
            "Login failure, please check the below...\n"
            "1. Please check the keys.\n"
            "2. IP address might not be match these keys.\n"
            "3. Got a response, but it is empty."
        )

        # display the current IP address
        response = requests.get("https://api.ipify.org")
        st.text(f"Current IP: {response.text}")
