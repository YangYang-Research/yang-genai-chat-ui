import base64
import streamlit as st
from helpers.loog import logger
from helpers.config import AppConfig, APIConfig
from helpers.http import MakeRequest

class AgentPage:
    def __init__(self):
        self.app_conf = AppConfig()
        self.api_conf = APIConfig()
        self.make_request = MakeRequest()

        @st.dialog("Agent Configuration", width="medium")
        def agent_configuration_dialog():
            agent = st.session_state.get("current_agent", None)
            if agent is None:
                st.write("No agent selected")
                return

            self.flexible_agent_dialog(agent)

        self.agent_configuration_dialog = agent_configuration_dialog

    def create_agent_logo_path(self, logo: str):
        # logo is like "anthropic.png"
        base_name = logo.rsplit('.', 1)[0]  # "anthropic"
        ext = logo.rsplit('.', 1)[-1]       # "png"
        if st.context.theme.type == "light":
            logo_filename = f"{base_name}-light.{ext}"
        else:
            logo_filename = f"{base_name}-dark.{ext}"
        return self.app_conf.agent_logo_folder_path / logo_filename
    
    def flexible_agent_dialog(self, agent: dict):
        # Fetch LLMs and sort them
        llms_resp_json = self.make_request.get(endpoint=self.api_conf.llm_endpoint)
        llms_sorted = sorted(llms_resp_json, key=lambda x: x["display_name"].lower())

        # Create display names with status
        def llm_display_with_status(llm):
            status_emoji = "🟢" if llm.get("status") == "enable" else "🔴"
            return f"{status_emoji} {llm['display_name']}"

        # Map LLM name <-> display (with status) and vice versa
        llm_name_to_display = {llm["name"]: llm_display_with_status(llm) for llm in llms_sorted}
        llm_display_to_name = {llm_display_with_status(llm): llm["name"] for llm in llms_sorted}
        all_llm_display_names = [llm_display_with_status(llm) for llm in llms_sorted]

        tools_resp_json = self.make_request.get(endpoint=self.api_conf.tool_endpoint)
        tools_sorted = sorted(tools_resp_json, key=lambda x: x["display_name"].lower())
        # Tool display with status
        def tool_display_with_status(tool):
            status_emoji = "🟢" if tool.get("status") == "enable" else "🔴"
            return f"{status_emoji} {tool['display_name']}"

        tool_name_to_display = {tool["name"]: tool_display_with_status(tool) for tool in tools_sorted}
        tool_display_to_name = {tool_display_with_status(tool): tool["name"] for tool in tools_sorted}
        all_tool_display_names = [tool_display_with_status(tool) for tool in tools_sorted]

        agent_logo_path = self.create_agent_logo_path(agent['logo'])
        base64_logo = base64.b64encode(open(agent_logo_path, "rb").read()).decode("utf-8")
        st.markdown(
            f"""
            <div style="text-align: left;">
                <h4><img src="data:image/png;base64,{base64_logo}" alt="{agent['display_name']}" style="width: 25px;"/> {agent['display_name']}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        dialog_key = f"agent_{agent['id']}_dialog_status"

        if dialog_key not in st.session_state:
            st.session_state[dialog_key] = agent["status"] == "enable"

        selected_index = 0 if st.session_state[dialog_key] else 1
        selected_status = st.radio(
            "Select status:",
            options=["Enable", "Disable"],
            index=selected_index,
            key=f"radio_{agent['id']}_dialog",
            horizontal=True,
        )

        input_name = st.text_input("Enter Agent Name:", key=f"name_{agent['id']}", value=agent.get('name', ''), disabled=True, help="The name is used as the key to identify the agent in the system. It cannot be changed.")
        input_display_name = st.text_input("Enter Agent Display Name:", key=f"display_name_{agent['id']}", value=agent.get('display_name', ''), help="The display name of the agent.")
        input_description = st.text_area("Enter Agent Description:", key=f"description_{agent['id']}", value=agent.get('description', ''), help="The description of the agent.")
        input_tags = st.multiselect(
            "Enter Agent Tags:",
            key=f"tags_{agent['id']}",
            accept_new_options=True,
            options=agent.get('tags', []),
            default=agent.get('tags', []),
            help="The tags of the agent.",
        )
        input_knowledge_base_id = st.text_input(
            "Enter Agent Knowledge Base ID:",
            key=f"knowledge_base_id_{agent['id']}",
            value=agent.get('knowledge_base_id', ''),
            help="The ID of the knowledge base for the agent.",
        )

        # Get agent llm names (support both id-object and name-string in the field)
        agent_llms = agent.get("llm_ids")
        agent_llm_names = []
        for entry in agent_llms:
            if isinstance(entry, dict) and "name" in entry:
                agent_llm_names.append(entry["name"])
            elif isinstance(entry, str):
                agent_llm_names.append(entry)
            elif isinstance(entry, int):
                # fallback, find name from id
                match = next((llm["name"] for llm in llms_sorted if llm.get("id") == entry), None)
                if match:
                    agent_llm_names.append(match)

        # Build default as [display_name (with status)] list
        default_llm_display_names = [llm_name_to_display[name] for name in agent_llm_names if name in llm_name_to_display]

        select_llm_for_agent = st.multiselect(
            "Select LLM for Agent:",
            options=all_llm_display_names,
            default=default_llm_display_names,
            key=f"selected_llm_for_agent_{agent['id']}",
            placeholder="Select LLM",
            help="The LLM to use for the agent.",
        )

        selected_llm_names = [llm_display_to_name[dn] for dn in select_llm_for_agent if dn in llm_display_to_name]
        input_system_prompt = st.text_area("Enter Agent System Prompt:", key=f"system_prompt_{agent['id']}", value=agent.get('system_prompt', ''), height=400, help="The system prompt for the agent.")

        agent_tools = agent.get("tools")
        agent_tool_names = []
        for entry in agent_tools:
            if isinstance(entry, dict) and "name" in entry:
                agent_tool_names.append(entry["name"])
            elif isinstance(entry, str):
                agent_tool_names.append(entry)
            elif isinstance(entry, int):
                # fallback, find name from id
                match = next((tool["name"] for tool in tools_sorted if tool.get("id") == entry), None)
                if match:
                    agent_tool_names.append(match)

        # Build default as [tool display_name (with status)] list
        default_tool_display_names = [tool_name_to_display[name] for name in agent_tool_names if name in tool_name_to_display]

        select_tools_for_agent = st.multiselect(
            "Select Tools for Agent:",
            options=all_tool_display_names,
            default=default_tool_display_names,
            key=f"selected_tools_for_agent_{agent['id']}",
            placeholder="Select Tools",
            help="The Tools to use for the agent.",
        )
        selected_tool_names = [tool_display_to_name[dn] for dn in select_tools_for_agent if dn in tool_display_to_name]
        default_agent = st.radio(
            "Default Agent:",
            options=["True", "False"],
            index=0 if agent.get('default_agent', False) else 1,
            key=f"agent_default_{agent['id']}",
            help="Whether this agent is the default agent for the system.",
        )

        if st.button("Save", key=f"save_{agent['id']}"):
            is_enable = selected_status == "Enable"
            st.session_state[dialog_key] = is_enable
            st.session_state[f"agent_{agent['id']}_enable_status"] = is_enable

            if is_enable and (not input_display_name or not input_description or not selected_llm_names or not default_agent):
                st.error("Display Name, Description, Selected LLMs, and Default Agent are required.")
                return
            else:
                payload = {
                    "name": agent["name"],
                    "display_name": input_display_name,
                    "description": input_description,
                    "tags": input_tags,
                    "knowledge_base_id": input_knowledge_base_id,
                    "llm_ids": [
                        {
                            "id": llm_item["id"],
                            "name": llm_item["name"]
                        }
                        for llm_item in llms_sorted 
                        if llm_item["name"] in selected_llm_names
                    ],
                    "tools": [
                        {
                            "id": tool_item["id"],
                            "name": tool_item["name"],
                            "status": tool_item.get("status", None)
                        }
                        for tool_item in tools_sorted 
                        if tool_item["name"] in selected_tool_names
                    ],
                    "default_agent": default_agent == "True",
                    "system_prompt": input_system_prompt,
                    "status": "enable" if is_enable else "disable",
                    "trashed": False,
                }
            resp_json = self.make_request.put(endpoint=self.api_conf.agent_endpoint + str(agent["id"]), data=payload)
            agent_id = resp_json.get("id", None)
            if agent_id is None:
                st.error("Failed to update agent configuration.")
                return
            
            st.session_state["agent_dialog_open"] = False
            st.session_state["current_agent"] = None

            st.success("Agent configuration updated successfully.")
            st.rerun()
    def render_agent_card(self, agent: dict):
        agent_id = agent["id"]
        card_key = f"agent_card_{agent_id}"
        agent_enable_status_key = f"agent_{agent_id}_enable_status"

        if agent_enable_status_key not in st.session_state:
            st.session_state[agent_enable_status_key] = agent["status"] == "enable"

        tags_html = "".join(
            f'<span style="background:#e0f2ff;color:#007bff;padding:3px 8px;margin-right:4px;border-radius:6px;font-size:11px;">{tag}</span>'
            for tag in agent["tags"]
        )

        with st.container(border=True, key=card_key):
            card_cols = st.columns([8, 2])
            agent_logo_path = self.create_agent_logo_path(agent['logo'])
            base64_logo = base64.b64encode(open(agent_logo_path, "rb").read()).decode("utf-8")

            with card_cols[0]:
                st.markdown(
                    f"""
                    <div style="text-align: left;">
                        <h3><img src="data:image/png;base64,{base64_logo}" alt="{agent['display_name']}" style="width: 30px;"/> {agent['display_name']}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with card_cols[1]:
                icon = "🟢" if st.session_state[agent_enable_status_key] else "🔴"
                if st.button(icon, key=f"{agent_enable_status_key}_widget"):
                    st.session_state["agent_dialog_open"] = True
                    st.session_state["current_agent"] = agent

            st.markdown(f"**Description:** {agent['description']}")
            st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)

    def display(self):
        st.title("Agents")
        st.caption("Configure the agents available for your AI assistant.", help="Agents allow your AI assistant to access external information and services to enhance its capabilities.")
        resp_json = self.make_request.get(endpoint=self.api_conf.agent_endpoint)
        agents_sorted = sorted(resp_json, key=lambda x: x["display_name"].lower())
        cols = st.columns(3)
        for i, agent in enumerate(agents_sorted):
            with cols[i % 3]:
                self.render_agent_card(agent)

        if st.session_state.get("agent_dialog_open", False):
            self.agent_configuration_dialog()

    def run(self):
        self.display()

def main():
    try:
        page = AgentPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()