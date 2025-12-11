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
        
        @st.dialog("LLM Configuration")
        def llm_configuration_dialog():
            llm = st.session_state.get("current_model", None)
            
            if llm is None:
                st.write("No LLM selected")
                return

            self.flexible_llm_dialog(llm)

        self.llm_configuration_dialog = llm_configuration_dialog

    def create_llm_logo_path(self, logo: str):
        # logo is like "anthropic.png"
        base_name = logo.rsplit('.', 1)[0]  # "anthropic"
        ext = logo.rsplit('.', 1)[-1]       # "png"
        if st.context.theme.type == "light":
            logo_filename = f"{base_name}-light.{ext}"
        else:
            logo_filename = f"{base_name}-dark.{ext}"
        return self.app_conf.llm_logo_folder_path / logo_filename

    def flexible_llm_dialog(self, llm: dict):
        llm_logo_path = self.create_llm_logo_path(llm['logo'])
        base64_logo = base64.b64encode(open(llm_logo_path, "rb").read()).decode("utf-8")
        st.markdown(
            f"""
            <div style="text-align: left;">
                <h4><img src="data:image/png;base64,{base64_logo}" alt="{llm['display_name']}" style="width: 25px;"/> {llm['display_name']}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        dialog_key = f"llm_{llm['id']}_dialog_status"

        # persist the radio state
        if dialog_key not in st.session_state:
            st.session_state[dialog_key] = llm["status"] == "enable"

        selected_index = 0 if st.session_state[dialog_key] else 1
        selected_action = st.radio(
            "Select action:",
            options=["Enable", "Disable"],
            index=selected_index,
            key=f"radio_{llm['id']}_dialog",
            horizontal=True,
        )

        input_model_name = st.text_input("Enter your Model Name:", key=f"model_name_{llm['id']}", value=llm.get('name', ''), disabled=True, help="The name is used as the key to identify the LLM in the system.")
        input_display_name = st.text_input("Enter your Display Name:", key=f"display_name_{llm['id']}", value=llm.get('display_name', ''), help="The display name of the LLM.")
        input_description = st.text_area("Enter your Description:", key=f"description_{llm['id']}", value=llm.get('description', ''), help="The description of the LLM.")
        input_provider = st.text_input("Enter your Provider:", key=f"provider_{llm['id']}", value=llm.get('provider', ''), help="The provider of the LLM on AWS Bedrock.")
        input_aws_region = st.text_input("Enter your AWS Region:", key=f"aws_region_{llm['id']}", value=llm.get('region', ''), help="The AWS region where the LLM is hosted on AWS Bedrock.")
        input_model_id = st.text_input("Enter your Model ID:", key=f"model_id_{llm['id']}", value=llm.get('model_id', ''), help="The ID of the LLM model on AWS Bedrock.")
        input_model_max_tokens = st.number_input("Enter your Model Max Tokens:", key=f"model_max_tokens_{llm['id']}", value=llm.get('max_tokens', 2048), min_value=1, max_value=12000, step=1, help="The maximum number of tokens that the LLM can generate on AWS Bedrock.")
        input_model_temperature = st.number_input("Enter your Model Temperature:", key=f"model_temperature_{llm['id']}", value=llm.get('temperature', 0.7), min_value=0.0, max_value=1.0, step=0.1, help="The temperature of the LLM on AWS Bedrock.")
        input_guardrail_id = st.text_input("Enter your Guardrail ID:", key=f"guardrail_id_{llm['id']}", value=llm.get('guardrail_id', ''), help="The ID of the Guardrail for the LLM on AWS Bedrock.")
        input_guardrail_version = st.text_input("Enter your Guardrail Version:", key=f"guardrail_version_{llm['id']}", value=llm.get('guardrail_version', ''), help="The version of the Guardrail for the LLM on AWS Bedrock.")
        input_system_prompt = st.text_area("Enter your System Prompt:", key=f"system_prompt_{llm['id']}", value=llm.get('system_prompt', ''), help="The system prompt for the LLM on AWS Bedrock.")
        
        if st.button("Save", key=f"save_{llm['id']}"):
            is_enable = selected_action == "Enable"
            st.session_state[dialog_key] = is_enable
            st.session_state[f"llm_{llm['id']}_enable_status"] = is_enable

            if is_enable and (not input_display_name or not input_description or not input_aws_region or not input_model_id or not input_model_max_tokens or not input_model_temperature):
                st.error("Display Name, Description, AWS Region, Model ID, Model Max Tokens, and Model Temperature are required.")
                return
            else:
                payload = {
                    "name": llm["name"],
                    "display_name": input_display_name,
                    "description": input_description,
                    "logo": llm["logo"],
                    "provider": input_provider,
                    "region": input_aws_region,
                    "model_id": input_model_id,
                    "model_max_tokens": str(input_model_max_tokens),
                    "model_temperature": str(input_model_temperature),
                    "guardrail_id": input_guardrail_id,
                    "guardrail_version": input_guardrail_version,
                    "system_prompt": input_system_prompt,
                    "status": "enable" if is_enable else "disable",
                    "trashed": False,
                }

            resp_json = self.make_request.put(endpoint=self.api_conf.llm_endpoint + str(llm["id"]), data=payload)
            llm_id = resp_json.get("id", None)
            if llm_id is None:
                st.error("Failed to update LLM configuration.")
                return

            st.session_state["llm_dialog_open"] = False
            st.session_state["current_model"] = None
            st.session_state["llm_dialog_type"] = None

            st.success("LLM configuration updated successfully.")
            st.rerun()

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
                    st.session_state["llm_dialog_open"] = True
                    st.session_state["current_model"] = llm

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
            self.llm_configuration_dialog()

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