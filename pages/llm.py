import base64
import streamlit as st
from helpers.loog import logger
from helpers.config import AppConfig, APIConfig
from helpers.http import MakeRequest

class LLMPage:
    def __init__(self):
        self.app_conf = AppConfig()
        self.api_conf = APIConfig()
        self.make_request = MakeRequest()
        
    def create_llm_logo_path(self, logo: str):
        # logo is like "anthropic.png"
        base_name = logo.rsplit('.', 1)[0]  # "anthropic"
        ext = logo.rsplit('.', 1)[-1]       # "png"
        if st.context.theme.type == "light":
            logo_filename = f"{base_name}-light.{ext}"
        else:
            logo_filename = f"{base_name}-dark.{ext}"
        return self.app_conf.llm_logo_folder_path / logo_filename

    def render_llm_card(self, llm: dict):
        llm_id = llm["id"]
        card_key = f"llm_card_{llm_id}"
        llm_enable_status_key = f"llm_{llm_id}_enable_status"

        if llm_enable_status_key not in st.session_state:
            st.session_state[llm_enable_status_key] = llm["status"] == "enable"

        with st.container(border=True, key=card_key):
            card_cols = st.columns([8, 2])
            llm_logo_path = self.create_llm_logo_path(llm['logo'])
            base64_logo = base64.b64encode(open(llm_logo_path, "rb").read()).decode("utf-8")

            with card_cols[0]:
                st.markdown(
                    f"""
                    <div style="text-align: left;">
                        <h3><img src="data:image/png;base64,{base64_logo}" alt="{llm['display_name']}" style="width: 30px;"/> {llm['display_name']}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with card_cols[1]:
                icon = "🟢" if st.session_state[llm_enable_status_key] else "🔴"
                if st.button(icon, key=f"{llm_enable_status_key}_widget"):  
                    pass

            st.markdown(f"**Description:** {llm['description']}")

    def display(self):
        st.title("🧠 LLMs")
        st.caption("Configure the LLMs available for your AI assistant.", help="LLMs allow your AI assistant to access external information and services to enhance its capabilities.")
        resp_json = self.make_request.get(endpoint=self.api_conf.llm_endpoint)
        llms_sorted = sorted(resp_json, key=lambda x: x["display_name"].lower())
        cols = st.columns(3)
        for i, llm in enumerate(llms_sorted):
            with cols[i % 3]:
                self.render_llm_card(llm)
        if st.session_state.get("llm_dialog_open", False):
            self.llm_dialog()

    def run(self):
        self.display()

def main():
    try:
        page = LLMPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()