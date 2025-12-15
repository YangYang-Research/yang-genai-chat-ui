import streamlit as st
from helpers.loog import logger
from helpers.http import MakeRequest
from helpers.config import AppConfig, APIConfig

class ToolPage:
    def __init__(self):
        self.app_conf = AppConfig()
        self.api_conf = APIConfig()
        self.make_request = MakeRequest()

        @st.dialog("Tool Configuration")
        def tool_configuration_dialog():
            tool = st.session_state.get("current_tool", None)
            dialog_type = st.session_state.get("tool_dialog_type", None)

            if tool is None or dialog_type is None:
                st.write("No tool selected")
                return

            self.flexible_tool_dialog(tool, dialog_type)

        self.tool_configuration_dialog = tool_configuration_dialog

    def flexible_tool_dialog(self, tool: dict, dialog_type: str):
        st.write(f"{tool['logo']} {tool['display_name']}")
        dialog_key = f"tool_{tool['id']}_dialog_status"

        # persist the radio state
        if dialog_key not in st.session_state:
            st.session_state[dialog_key] = tool["status"] == "enable"

        selected_index = 0 if st.session_state[dialog_key] else 1
        selected_status = st.radio(
            "Select status:",
            options=["Enable", "Disable"],
            index=selected_index,
            key=f"radio_{tool['id']}_dialog",
            horizontal=True,
        )

        if dialog_type == "A":
            pass
        elif dialog_type == "B":
            input_api_key = st.text_input("Enter your API Key:", key=f"api_{tool['id']}", value=tool.get('api_key', ''))
            input_cse_id = st.text_input("Enter your CSE ID:", key=f"cse_{tool['id']}", value=tool.get('cse_id', ''))
        elif dialog_type == "C":
            input_api_key = st.text_input("Enter your API Key:", key=f"api_{tool['id']}", value=tool.get('api_key', ''))
        elif dialog_type == "D":
            input_client_id = st.text_input("Enter your Client ID:", key=f"client_id_{tool['id']}", value=tool.get('client_id', ''))
            input_client_secret = st.text_input("Enter your Client Secret:", key=f"client_secret_{tool['id']}", value=tool.get('client_secret', ''), type="password")
        elif dialog_type == "E":
            input_client_id = st.text_input("Enter your Reddit Client ID:", key=f"reddit_client_id_{tool['id']}", value=tool.get('client_id', ''))
            input_client_secret = st.text_input("Enter your Reddit Client Secret:", key=f"reddit_client_secret_{tool['id']}", value=tool.get('client_secret', ''), type="password")
            input_user_agent = st.text_input("Enter your Reddit User Agent:", key=f"reddit_user_agent_{tool['id']}", value=tool.get('user_agent', ''))
        elif dialog_type == "F":
            input_host = st.text_input("Enter your Searx Instance URL:", key=f"host_instance_{tool['id']}", value=tool.get('host', ''))
        else:
            pass

        # Save button
        if st.button("Save", key=f"save_{tool['id']}"):
            is_enable = selected_status == "Enable"
            st.session_state[dialog_key] = is_enable
            st.session_state[f"tool_{tool['id']}_enable_status"] = is_enable

            if dialog_type == "A":
                pass
            elif dialog_type == "B":
                if is_enable and not input_api_key or not input_cse_id:
                    st.error("API Key and CSE ID are required.")
                    return
            elif dialog_type == "C":
                if is_enable and not input_api_key:
                    st.error("API Key is required.")
                    return
            elif dialog_type == "D":
                if is_enable and not input_client_id or not input_client_secret:
                    st.error("Client ID and Client Secret are required.")
                    return
            elif dialog_type == "E":
                if is_enable and not input_client_id or not input_client_secret or not input_user_agent:
                    st.error("Reddit Client ID, Client Secret, and User Agent are required.")
                    return
            elif dialog_type == "F":
                if is_enable and not input_host:
                    st.error("Searx Instance URL is required.")
                    return
            else:
                pass

            payload = {
                "name": tool["name"],
                "display_name": tool["display_name"],
                "logo": tool["logo"],
                "description": tool["description"],
                "tags": tool["tags"],
                "status": "enable" if is_enable else "disable",
                "trashed": False,
                "host": input_host if 'input_host' in locals() else None,
                "api_key": input_api_key if 'input_api_key' in locals() else None,
                "cse_id": input_cse_id if 'input_cse_id' in locals() else None,
                "client_id": input_client_id if 'input_client_id' in locals() else None,
                "client_secret": input_client_secret if 'input_client_secret' in locals() else None,
                "user_agent": input_user_agent if 'input_user_agent' in locals() else None
            }

            resp_json, status_code = self.make_request.put(endpoint=self.api_conf.tool_endpoint + str(tool["id"]), data=payload)
            if status_code == 200:
                st.session_state["tool_dialog_open"] = False
                st.session_state["current_tool"] = None
                st.session_state["tool_dialog_type"] = None

                st.success("Tool configuration updated successfully.")
                st.rerun()
            else:
                st.error("Failed to update tool configuration. Traceback: " + resp_json.get("detail"))
                st.rerun()            

    def render_tool_card(self, tool: dict):
        tool_id = tool["id"]
        card_key = f"tool_card_{tool_id}"
        tool_enable_status_key = f"tool_{tool_id}_enable_status"

        if tool_enable_status_key not in st.session_state:
            st.session_state[tool_enable_status_key] = tool["status"] == "enable"

        tags_html = "".join(
            f'<span style="background:#e0f2ff;color:#007bff;padding:3px 8px;margin-right:4px;border-radius:6px;font-size:11px;">{tag}</span>'
            for tag in tool["tags"]
        )

        with st.container(border=True, key=card_key):
            card_cols = st.columns([8, 2])
            with card_cols[0]:
                st.markdown(f"#### {tool['logo']} {tool['display_name']}")
            with card_cols[1]:
                icon = "🟢" if st.session_state[tool_enable_status_key] else "🔴"
                if st.button(icon, key=f"{tool_enable_status_key}_widget"):
                    st.session_state["tool_dialog_open"] = True
                    st.session_state["current_tool"] = tool

                    if tool["name"] in ["arxiv", "duckduckgo", "wikipedia"]:
                        st.session_state["tool_dialog_type"] = "A"
                    elif tool["name"] == "google_search":
                        st.session_state["tool_dialog_type"] = "B"
                    elif tool["name"] in ["google_scholar", "google_trends", "openweather"]:
                        st.session_state["tool_dialog_type"] = "C"
                    elif tool["name"] == "asknews":
                        st.session_state["tool_dialog_type"] = "D"
                    elif tool["name"] == "reddit":
                        st.session_state["tool_dialog_type"] = "E"
                    elif tool["name"] == "searx":
                        st.session_state["tool_dialog_type"] = "F"
                    else:
                        st.session_state["tool_dialog_type"] = "Z"

            st.markdown(f"**Description:** {tool['description']}")
            st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)

    def display(self):
        st.title("🛠️ Tools")
        st.caption("Configure the tools available for your AI assistant.", help="Tools allow your AI assistant to access external information and services to enhance its capabilities.")
        resp_json, _ = self.make_request.get(endpoint=self.api_conf.tool_endpoint)
        tools_sorted = sorted(resp_json, key=lambda x: x["display_name"].lower())
        cols = st.columns(4)

        for i, tool in enumerate(tools_sorted):
            with cols[i % 4]:
                self.render_tool_card(tool)
                
        if st.session_state.get("tool_dialog_open", False):
            self.tool_configuration_dialog()

    def run(self):
        self.display()


def main():
    try:
        page = ToolPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)


if __name__ == "__main__":
    main()
