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
        def universal_dialog():
            tool = st.session_state.get("current_tool", None)
            dialog_type = st.session_state.get("dialog_type", None)

            if tool is None or dialog_type is None:
                st.write("No tool selected")
                return

            if dialog_type == "A":
                self.custom_dialog_a(tool)
            elif dialog_type == "B":
                self.custom_dialog_b(tool)
            elif dialog_type == "C":
                self.custom_dialog_c(tool)
            else:
                st.write("Dialog type Z")

        self.universal_dialog = universal_dialog

    def custom_dialog_a(self, tool):
        st.write(f"{tool['logo']} {tool['display_name']}")
        dialog_key = f"tool_{tool['id']}_dialog_status"

        # persist trạng thái radio
        if dialog_key not in st.session_state:
            st.session_state[dialog_key] = tool["status"] == "enable"

        selected_index = 0 if st.session_state[dialog_key] else 1
        selected_action = st.radio(
            "Select action:",
            options=["Enable", "Disable"],
            index=selected_index,
            key=f"radio_{tool['id']}_dialog",
            horizontal=True,
        )

        # Save button
        if st.button("Save", key=f"save_{tool['id']}"):
            is_enable = selected_action == "Enable"
            st.session_state[dialog_key] = is_enable
            st.session_state[f"tool_{tool['id']}_enable_status"] = is_enable

            # Đóng dialog
            st.session_state["dialog_open"] = False
            st.session_state["current_tool"] = None
            st.session_state["dialog_type"] = None

            st.success(f"Tool '{tool['display_name']}' updated to {selected_action}")
            st.rerun()  # rerun sau khi save

    def custom_dialog_b(self, tool):
        st.write(f"{tool['logo']} {tool['display_name']}")
        dialog_key = f"tool_{tool['id']}_dialog_status"

        if dialog_key not in st.session_state:
            st.session_state[dialog_key] = tool["status"] == "enable"

        input_api_key = st.text_input("Enter your API Key:", key=f"api_{tool['id']}")
        input_cse_id = st.text_input("Enter your CSE ID:", key=f"cse_{tool['id']}")

        selected_action = st.radio(
            "Select action:",
            options=["Enable", "Disable"],
            index=0 if st.session_state[dialog_key] else 1,
            key=f"radio_{tool['id']}_dialog",
            horizontal=True,
        )

        if st.button("Save", key=f"save_{tool['id']}"):
            if input_api_key and input_cse_id:
                st.session_state[dialog_key] = selected_action == "Enable"
                card_key = f"tool_{tool['id']}_card_status"
                st.session_state[card_key] = selected_action == "Enable"

                st.session_state["dialog_open"] = False
                st.session_state["current_tool"] = None
                st.session_state["dialog_type"] = None

                st.success(f"Tool '{tool['display_name']}' configured and enabled.")
                st.rerun()
            else:
                st.error("Please provide both API Key and CSE ID.")

    # --------------------- Dialog C ---------------------
    def custom_dialog_c(self, tool):
        st.write(f"{tool['logo']} {tool['display_name']}")
        dialog_key = f"tool_{tool['id']}_dialog_status"

        if dialog_key not in st.session_state:
            st.session_state[dialog_key] = tool["status"] == "enable"

        input_api_key = st.text_input("Enter your API Key:", key=f"api_c_{tool['id']}")

        if st.button("Save", key=f"save_{tool['id']}"):
            if input_api_key:
                st.session_state[dialog_key] = True
                card_key = f"tool_{tool['id']}_card_status"
                st.session_state[card_key] = True

                st.session_state["dialog_open"] = False
                st.session_state["current_tool"] = None
                st.session_state["dialog_type"] = None

                st.success(f"Tool '{tool['display_name']}' configured and enabled.")
                st.rerun()
            else:
                st.error("Please provide API Key.")

    def render_tool_card(self, tool):
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
                    st.session_state["dialog_open"] = True
                    st.session_state["current_tool"] = tool

                    if tool["name"] in ["arxiv", "duckduckgo", "wikipedia"]:
                        st.session_state["dialog_type"] = "A"
                    elif tool["name"] == "google_search":
                        st.session_state["dialog_type"] = "B"
                    elif tool["name"] in ["google_scholar", "google_trends"]:
                        st.session_state["dialog_type"] = "C"
                    else:
                        st.session_state["dialog_type"] = "Z"

            st.markdown(f"**Description:** {tool['description']}")
            st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)

    def display(self):
        st.title("🛠️ Tools")
        resp_json = self.make_request.get(endpoint=self.api_conf.tool_endpoint)
        tools_sorted = sorted(resp_json, key=lambda x: x["display_name"].lower())
        cols = st.columns(4)

        for i, tool in enumerate(tools_sorted):
            with cols[i % 4]:
                self.render_tool_card(tool)
                
        if st.session_state.get("dialog_open", False):
            self.universal_dialog()

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
