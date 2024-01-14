import requests
import streamlit as st

from src.client import UpbitAccount


class LoginManager:
    """Connect to Upbit account.

    Reference:
        https://docs.upbit.com/docs/create-authorization-request
    """

    name = "Access Keys"
    icon = "gear"

    @staticmethod
    def run() -> None:
        """Display info."""
        st.title("Upbit Account")
        access_key = st.text_input(label="Access Key")
        secret_key = st.text_input(label="Secret Key", type="password")

        if st.button("Access!"):
            try:
                account = UpbitAccount(access_key=access_key, secret_key=secret_key)
                st.text("Success to load.")
                st.subheader("Account INFO")
                st.code(account.get_info(n_info=3))
            except:
                st.text(
                    "Failed to load ...\n" "IP address might not be match these keys."
                )

                # display the current IP address
                response = requests.get("https://api.ipify.org")
                st.text(f"Current IP: {response.text}")
