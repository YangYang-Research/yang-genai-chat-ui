import uuid
import streamlit as st
from helpers.config import AppConfig
from helpers.auth import get_logout, get_user_info, check_user_login
from helpers.loog import logger

# ------------- Application Class -------------
class App:
    def __init__(self):
        self.config = AppConfig()

    def _set_page_config(self):
        st.set_page_config(
            page_title=self.config.page_title,
            page_icon=self.config.favicon_path,
            layout="wide",
        )
    
    def _set_header(self):
        st.logo(self.config.logo_path, size="large", icon_image=self.config.logo_path)

    def _init_session_state(self):
        if "authentication_status" not in st.session_state:
            st.session_state["authentication_status"] = None
        if "chat_session_id" not in st.session_state:
            st.session_state["chat_session_id"] = None
        if "userinfo" not in st.session_state:
            st.session_state["userinfo"] = None

    def logout_page(self):
        get_logout()
        st.rerun()

    def run(self):
        self._set_page_config()
        self._set_header()
        self._init_session_state()

        # Define pages
        home_page = st.Page("pages/home.py", title="Home", icon="🚀", url_path="/")
        agent_page = st.Page("pages/agent.py", title="Yang Agent", icon="💬", url_path="/yang-agent")
        tool_page = st.Page("pages/tool.py", title="Tools", icon="🛠️", url_path="/tools")

        user_page = st.Page("pages/user.py", title="User", icon="👤", url_path="/user")

        blank_page = st.Page("pages/blank.py", title="Blank", icon="📄", url_path="/blank")

        login_page = st.Page("pages/login.py", title="Login", icon="🔐", url_path="/login")
        logout_page = st.Page("pages/logout.py", title="Logout", icon="🚪", url_path="/logout")

        if st.session_state.get("authentication_status") or check_user_login(extend_key="app-check-login"):
            user_info = get_user_info(extend_key="app-after-auth")

            if st.session_state.get("chat_session_id") is None:
                st.session_state["chat_session_id"] = uuid.uuid1()

            pg = st.navigation({
                "Yang": [home_page, agent_page, tool_page],
                "Account": [user_page, logout_page],
                "Pages": [blank_page],
            }, position="top")

        else:
            pg = st.navigation({
                "Account": [login_page]
            })

        pg.run()

# ------------- Main Execution -------------
def main():
    try:
        app = App()
        app.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()
