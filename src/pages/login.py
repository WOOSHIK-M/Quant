import json
import uuid

import jwt
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

UPBIT_OPEN_API_ACCOUNT_URL = "https://api.upbit.com/v1/accounts"


class LoginManager:
    """Connect to Upbit account.

    Reference:
        https://docs.upbit.com/docs/create-authorization-request
    """

    name = "Access Keys"
    icon = "gear"

    @staticmethod
    def run() -> None:
        """Run a login page."""
        login_manager = LoginManager()

        # get two keys to access the account
        st.title("Upbit Account")
        access_key = st.text_input(label="Access Key")
        secret_key = st.text_input(label="Secret Key", type="password")

        # make a button to login
        if st.button("Access!"):
            success_to_login, account_info = login_manager.get_account_info(
                access_key, secret_key
            )
            if success_to_login:
                login_manager.display_account_info(account_info)
            else:
                login_manager.display_incorrect_login()

    def get_account_info(self, access_key: str, secret_key: str) -> tuple[bool, dict]:
        """Get account information."""
        payload = {"access_key": access_key, "nonce": str(uuid.uuid4())}
        token = jwt.encode(payload=payload, key=secret_key)

        response = requests.get(
            url=UPBIT_OPEN_API_ACCOUNT_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code in [400, 401]:
            return False, {}
        if response.text is None:
            return False, {}
        return True, json.loads(response.text)

    def display_account_info(self, account_info: dict) -> None:
        """Display the current account information."""
        st.subheader("Account INFO.")

        df = pd.DataFrame(account_info)

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
