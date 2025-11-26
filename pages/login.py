import streamlit as st
import uuid
import base64
from helpers.config import AppConfig, APIConfig
from helpers.loog import logger
from helpers.http import MakeRequest
from passlib.context import CryptContext
from helpers.auth import verify_jwt_token, create_jwt_cookie

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class LoginPage:
    def __init__(self):
        self.app_conf = AppConfig()
        self.api_conf = APIConfig()
        self.make_request = MakeRequest()

    def display(self):
        st.logo(self.app_conf.logo_path, size="large", icon_image=self.app_conf.logo_path)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            base64_logo = base64.b64encode(open(self.app_conf.logo_path, "rb").read()).decode("utf-8")
            st.markdown(
                f"""
                <div style="text-align: left;">
                    <h2><img src="data:image/png;base64,{base64_logo}" alt="Logo" style="width: 100px;"/>{self.app_conf.app_name}</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

            username_input = st.text_input("Username", value="administrator")
            password_input = st.text_input("Password", type="password", value="ee048b39821018e97276c6dfd16840dd")

            if st.button("Login"):
                if not username_input or not password_input:
                    st.error("Please enter username and password.")
                    return

                resp_json = self.make_request.post(endpoint=self.api_conf.login_endpoint, data={
                    "username": username_input,
                    "password": password_input
                })

                jwt_token = resp_json.get("jwt_token")

                user_info = verify_jwt_token(jwt_token)

                if jwt_token and user_info:
                    st.session_state["authentication_status"] = True

                if st.session_state.get("authentication_status"):
                    create_jwt_cookie(jwt_token)
                    st.session_state["userinfo"] = user_info
                    st.session_state["chat_session_id"] = uuid.uuid1()
                    st.success("Login successful!")
                    st.rerun()
                elif st.session_state.get("authentication_status") is False:
                    st.error("Username/password is incorrect")
                else:
                    st.info("Please enter your username and password")

    def run(self):
        self.display()
    
def main():
    try:
        page = LoginPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()