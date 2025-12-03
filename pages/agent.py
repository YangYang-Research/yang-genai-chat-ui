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

def init_session_state(default_model: str = "claude"):
    """Initialize session state."""
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}  # {message_index: "up"/"down"}
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = default_model

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

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        options = api_conf.chat_model_support

        if st.session_state.selected_model not in options:
            st.session_state.selected_model = options[0] if options else ""

        selected_model = st.selectbox(
            "Models:",
            options,
            index=options.index(st.session_state.selected_model),
            placeholder="Select model",
            key="model_selector",
            help="Select the chat model to use.",
        )

        # Update session_state when user changes selection
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.toast(f"Model selected: {selected_model}", icon="✅")

    return st.session_state.selected_model

class AgentPage:
    def __init__(self):
        pass
    
    def display(self):
        st.markdown("### 💬 Yang Agent")
        
        init_session_state(default_model="claude")

        chat_model = render_model_selector()

        msgs = StreamlitChatMessageHistory(key="chat_history")

        if not msgs.messages:
            msgs.add_ai_message("👋 Hello! How can I assist you today?")

        # Display chat history
        for idx, msg in enumerate(msgs.messages):
            role = "assistant" if msg.type == "ai" else "user"

            if role == "user":
                st.chat_message("user").write(msg.content)
            else:
                # Feedback for assistant messages only
                with st.chat_message("assistant"):
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
            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                for chunk in make_request.stream_chat_completions(chat_model, msgs, prompt, attachments):
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
        page = AgentPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()
