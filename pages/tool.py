import streamlit as st
from helpers.loog import logger
from helpers.http import MakeRequest
from helpers.config import AppConfig, APIConfig


class ToolPage:
    def __init__(self):
        self.app_conf = AppConfig()
        self.api_conf = APIConfig()
        self.make_request = MakeRequest()

        @st.dialog("Update Tool")
        def custom_dialog_enable_disable(tool):
            st.write(f"{tool['logo']} {tool['display_name']}")

            btn_key = f"btn_{tool['id']}"
            pending_key = f"{btn_key}_pending"
            dialog_open_key = f"dialog_open_{tool['id']}"

            if pending_key not in st.session_state:
                st.session_state[pending_key] = st.session_state.get(btn_key, True)
            st.session_state[dialog_open_key] = True

            selected_action = st.radio(
                "Select action:",
                options=["Enable", "Disable"],
                index=0 if st.session_state[pending_key] else 1,
                key=f"radio_{tool['id']}",
                horizontal=True,
                help="Choose to enable or disable the tool.",
            )

            if st.button("Save", key=f"save_{tool['id']}"):
                new_val = selected_action == "Enable"
                st.session_state[btn_key] = new_val 
                st.session_state[pending_key] = new_val
                st.session_state[dialog_open_key] = False
                st.success(f"Tool '{tool['display_name']}' updated to {selected_action}")
                st.rerun()

        @st.dialog("Update Tool")
        def custom_dialog_b(tool):
            st.write(f"This is custom dialog B for **{tool['display_name']}**")
            reason = st.text_input("Reason for toggle (optional)", key=f"reason_b_{tool['id']}")
            if st.button("Confirm B", key=f"confirm_b_{tool['id']}"):
                st.session_state[f"tool_{tool['id']}_confirmed"] = True
                st.session_state[f"tool_{tool['id']}_reason"] = reason
                st.rerun()
            if st.button("Cancel B", key=f"cancel_b_{tool['id']}"):
                st.session_state[f"toggle_{tool['id']}"] = not st.session_state.get(f"toggle_{tool['id']}", True)
                st.rerun()

        self.custom_dialog_enable_disable = custom_dialog_enable_disable
        self.dialog_b = custom_dialog_b

    def render_tool_card(self, tool):
        disabled = tool["status"] != "enable"
        card_key = f"tool_{tool['id']}"
        btn_key = f"btn_{tool['id']}"

        tags_html = "".join(
            f'<span style="background:#e0f2ff;color:#007bff;padding:3px 8px;margin-right:4px;border-radius:6px;font-size:11px;">{tag}</span>'
            for tag in tool["tags"]
        )

        with st.container(border=True, key=card_key):
            card_cols = st.columns([8, 2])
            with card_cols[0]:
                st.markdown(f"#### {tool['logo']} {tool['display_name']}")
            with card_cols[1]:
                btn_key = f"btn_{tool['id']}"
                pending_key = f"{btn_key}_pending"

                if btn_key not in st.session_state:
                    st.session_state[btn_key] = not disabled

                icon = "🟢" if st.session_state[btn_key] else "🔴"

                if st.button(icon, key=f"{btn_key}_widget", help="Click to update tool."):
                    st.session_state[f"dialog_open_{tool['id']}"] = True


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

                btn_key = f"btn_{tool['id']}"
                pending_key = f"{btn_key}_pending"
                dialog_open_key = f"dialog_open_{tool['id']}"

                if btn_key not in st.session_state:
                    st.session_state[btn_key] = tool["status"] == "enable"
                if pending_key not in st.session_state:
                    st.session_state[pending_key] = st.session_state[btn_key]
                if dialog_open_key not in st.session_state:
                    st.session_state[dialog_open_key] = False

                if st.session_state.get(dialog_open_key, False):
                    if tool["name"] == "arxiv":
                        self.custom_dialog_enable_disable(tool)
                    elif tool["name"] == "asknew":
                        self.dialog_b(tool)

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
