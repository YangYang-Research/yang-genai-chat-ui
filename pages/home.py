import base64
import streamlit as st
from helpers.loog import logger
from helpers.utils import Utils
from helpers.http import MakeRequest
from helpers.config import AppConfig, AWSConfig, APIConfig
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

app_conf = AppConfig()
aws_conf = AWSConfig()
api_conf = APIConfig()
make_request = MakeRequest()
utils = Utils()

def init_session_state():
    """Initialize session state."""
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}  # {message_index: "up"/"down"}
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None
    if "agent_name" not in st.session_state:
        st.session_state.agent_name = None
    if "agent_display_name" not in st.session_state:
        st.session_state.agent_display_name = None
    if "agent_logo" not in st.session_state:
        st.session_state.agent_logo = None
    if "agent_logo_path" not in st.session_state:
        st.session_state.agent_logo_path = None

def save_feedback(message_index: int):
    """Save user feedback and send to backend."""
    key = f"feedback_{message_index}"
    user_feedback = st.session_state.get(key, None)

    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    st.session_state.feedback[message_index] = user_feedback

    # Retrieve message content (safe lookup)
    msgs = st.session_state.get("chat_history", None)
    if isinstance(msgs, list):
        if 0 <= message_index < len(msgs):
            message_content = getattr(msgs[message_index], "content", None)
    elif hasattr(msgs, "messages"):
        all_msgs = getattr(msgs, "messages", [])
        if 0 <= message_index < len(all_msgs):
            message_content = getattr(all_msgs[message_index], "content", None)
    
    logger.info(f"[Feedback] Message {message_index} => {user_feedback}")
    try:
        if message_content:
            make_request.post(
                endpoint=api_conf.chat_feedback_endpoint,
                data={
                    "message_index": message_index,
                    "message_content": message_content,
                    "feedback": user_feedback,
                },
            )
        else:
            logger.warning(f"[Feedback] No content found for message {message_index}")
    except Exception as e:
        logger.error(f"[Feedback] Failed to send feedback: {e}")

def render_model_selector():
    """Render model selector with session persistence."""

    llms_resp_json = make_request.get(endpoint=api_conf.llm_endpoint + "enabled")
    llms_sorted = sorted(llms_resp_json, key=lambda x: x["display_name"].lower())
    # Create options as (display_name, name) pairs for display/value separation
    model_options = [(llm["display_name"], llm["name"]) for llm in llms_sorted]
    name_to_display = {llm["name"]: llm["display_name"] for llm in llms_sorted}
    names = [llm["name"] for llm in llms_sorted]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.session_state.selected_model not in names:
            st.session_state.selected_model = names[0] if names else ""

        # Set up index for selectbox
        current_idx = names.index(st.session_state.selected_model) if st.session_state.selected_model in names else 0

        # Display display_name, but internally value is name
        selected_display = st.selectbox(
            "LLMs:",
            options=model_options,
            index=current_idx,
            format_func=lambda pair: pair[0],
            placeholder="Select LLM",
            key="model_selector",
            help="Select the LLM to use.",
        )

        selected_model = selected_display[1]  # Take name value

        # Update session_state when user changes selection
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.toast(f"LLM selected: {name_to_display[selected_model]}", icon="✅")

    return st.session_state.selected_model

def create_agent_logo_path(logo: str):
    # logo is like "anthropic.png"
    base_name = logo.rsplit('.', 1)[0]  # "anthropic"
    ext = logo.rsplit('.', 1)[-1]       # "png"
    if st.context.theme.type == "light":
        logo_filename = f"{base_name}-light.{ext}"
    else:
        logo_filename = f"{base_name}-dark.{ext}"
    return app_conf.agent_logo_folder_path / logo_filename

class HomePage:
    def __init__(self):
        pass
    
    def display(self):
        agent_resp_json = make_request.get(endpoint=api_conf.agent_endpoint + "default")
        agent_name = agent_resp_json.get("name", None)
        if agent_name is not None:
            st.session_state.agent_name = agent_name
            st.session_state.agent_display_name = agent_resp_json.get("display_name", None)
            st.session_state.agent_logo = agent_resp_json.get("logo", None)
            st.session_state.agent_logo_path = create_agent_logo_path(st.session_state.agent_logo)
        else:
            st.error("No default agent found.")
            st.stop()

        base64_logo = base64.b64encode(open(st.session_state.agent_logo_path, "rb").read()).decode("utf-8")
        st.markdown(f"### <img src='data:image/png;base64,{base64_logo}' alt='{st.session_state.agent_display_name}' style='width: 40px;'/> {st.session_state.agent_display_name}", unsafe_allow_html=True)

        init_session_state()

        chat_model = render_model_selector()

        msgs = StreamlitChatMessageHistory(key="chat_history")

        # if not msgs.messages:
        #     msgs.add_ai_message("👋 Hello! How can I assist you today?")

        # Display chat history
        for idx, msg in enumerate(msgs.messages):
            role = "assistant" if msg.type == "ai" else "user"

            if role == "user":
                st.chat_message("user").write(msg.content)
            else:
                # Feedback for assistant messages only
                with st.chat_message("assistant", avatar=st.session_state.get("agent_logo_path", app_conf.agent_logo_path)):
                    st.write(msg.content)
                    existing_feedback = st.session_state.feedback.get(idx)
                    st.session_state[f"feedback_{idx}"] = existing_feedback
                    st.feedback(
                        "thumbs",
                        key=f"feedback_{idx}",
                        disabled=existing_feedback is not None,
                        on_change=save_feedback,
                        args=[idx],
                    )

        # Input box
        if message := st.chat_input("Type your message here...", accept_file="multiple", file_type=["txt", "pdf", "docx", "png", "jpg", "jpeg", "csv", "xlsx"]):

            prompt = message["text"]
            files = message["files"]
            attachments = []
            
            if not prompt:
                st.warning("Please enter a message.")
                st.stop()
            
            if files:
                attachments = utils.process_multiple_files(files)
            
            msgs.add_user_message(prompt)
            st.chat_message("user").write(prompt)

            if files:
                for attachment in attachments:
                    if attachment.is_image:
                        st.image(image=attachment.bytes, width=100)
                        st.write(f"Attachment: {attachment.name} - {attachment.size_kb} KB")
                    else:
                        st.write(f"Attachment: {attachment.name} - {attachment.size_kb} KB")

            # Stream AI response
            with st.chat_message("assistant", avatar=st.session_state.get("agent_logo_path", app_conf.agent_logo_path)):
                placeholder = st.empty()
                full_response = ""
                for chunk in make_request.stream_chat_completions(agent_name=st.session_state.agent_name, chat_model=chat_model, history=msgs, prompt=prompt, attachments=attachments):
                    full_response += chunk
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)

                msgs.add_ai_message(full_response)
                
                # Feedback for new AI message
                idx = len(msgs.messages) - 1
                st.session_state[f"feedback_{idx}"] = None
                st.feedback(
                    "thumbs",
                    key=f"feedback_{idx}",
                    on_change=save_feedback,
                    args=[idx],
                )

    def run(self):
        self.display()

def main():
    try:
        page = HomePage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()
