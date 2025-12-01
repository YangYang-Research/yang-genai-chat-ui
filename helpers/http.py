import requests
import streamlit as st
from helpers.loog import logger
from helpers.secret import AWSSecretManager
from helpers.utils import Utils
from helpers.config import AppConfig, AWSConfig, APIConfig

class MakeRequest(object):
    def __init__(self):
        self.app_conf = AppConfig()
        self.aws_conf = AWSConfig()
        self.api_conf = APIConfig()
        self.aws_secret_manager = AWSSecretManager()

    def stream_chat_completions(self, chat_model: str, history: dict, prompt: str, attachments: list):
        """
        Stream tokens from backend API (StreamingResponse).
        """

        messages = []

        if chat_model == "claude":
            messages = [
                    {"role": "user" if m.type == "human" else "assistant", "content": m.content}
                    for m in history.messages
                ]
        
            if attachments:
                for attachment in attachments:
                    if attachment.status.value == "completed":
                        if attachment.is_image and attachment.base64:
                            messages = messages + [
                                {
                                    "role": "user", 
                                    "content": [
                                        {
                                            "type": "text", 
                                            "text": prompt
                                        },
                                        {
                                            "type": "image",
                                            "source": {
                                                "type": "base64",
                                                "media_type": attachment.type,
                                                "data": attachment.base64,
                                            },
                                        },
                                    ]
                                }
                            ]
                        elif attachment.is_document and attachment.base64:
                            messages = messages + [
                                {
                                    "role": "user", 
                                    "content": [
                                        {
                                            "type": "text", 
                                            "text": prompt
                                        },
                                        {
                                            "document": {
                                                # Available formats: html, md, pdf, doc/docx, xls/xlsx, csv, and txt
                                                "format": Utils.get_file_format(attachment.type),
                                                "name": Utils.format_filename(attachment.name),
                                                "source": {"bytes": attachment.base64}, #(convert bytes → base64 string) for sending over HTTP
                                            }
                                        },
                                    ]
                                }
                            ]
                        elif attachment.is_text and attachment.content:
                            messages = messages + [
                                {
                                    "role": "user", 
                                    "content": [
                                        {
                                            "type": "text", 
                                            "text": prompt
                                        },
                                        {
                                            "type": "text", 
                                            "text": attachment.content
                                        },
                                    ]
                                }
                            ]
                        else:
                            pass
            else:
                messages = messages + [{"role": "user", "content": prompt}]
        elif chat_model == "llama":
            st.toast(f"Model : {chat_model} currently not supported", icon="⚠️")
            st.stop()
        elif chat_model == "gpt-oss":
            st.toast(f"Model : {chat_model} currently not supported", icon="⚠️")
            st.stop()
        else:
            st.toast(f"Model : {chat_model} currently not supported", icon="⚠️")
            st.stop()

        if isinstance(messages, tuple):
            messages = list(messages)

        chat_session = st.session_state.get("chat_session_id")

        payload = {
            "chat_session_id": str(chat_session),
            "model_name": chat_model,
            "messages": messages,
        }

        headers = {
            "Content-Type": "application/json",
            "x-yang-auth": f"Basic {self.aws_secret_manager.get_secret(self.api_conf.api_auth_key_name)}",
        }

        try:
            with requests.post(self.api_conf.api_service + self.api_conf.chat_agent_completions_endpoint, headers=headers, json=payload, stream=True, timeout=self.api_conf.api_timeout_seconds) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk.decode("utf-8")
        except requests.exceptions.RequestException as e:
            logger.error(f"[FE->BE] Stream error: {e}")
            yield f"\n[Error] Unable connect to backend service. Please try again."
    
    def post_streaming(self, endpoint: str, data: dict):
        """
        Send a POST request to the specified endpoint with the given data.
        """
        headers = {
            "Content-Type": "application/json",
            "x-yang-auth": f"Basic {self.aws_secret_manager.get_secret(self.api_conf.api_auth_key_name)}",
        }
        try:
            response = requests.post(self.api_conf.api_service + endpoint, headers=headers, json=data, timeout=self.api_conf.api_timeout_seconds)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"[FE->BE] POST error: {e}")
            yield f"\n[Error] Unable connect to backend service. Please try again."
    
    def get(self, endpoint: str, param: str | int = None):
        """
        Send a GET request to the specified endpoint with optional parameter.
        """
        headers = {
            "Content-Type": "application/json",
            "x-yang-auth": f"Basic {self.aws_secret_manager.get_secret(self.api_conf.api_auth_key_name)}",
        }        
        try:
            response = requests.get(self.api_conf.api_service + endpoint, headers=headers, params=param, timeout=self.api_conf.api_timeout_seconds)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"[FE->BE] GET error: {e}")
    
    def post(self, endpoint: str, data: dict):
        """
        Send a POST request to the specified endpoint.
        """
        headers = {
            "Content-Type": "application/json",
            "x-yang-auth": f"Basic {self.aws_secret_manager.get_secret(self.api_conf.api_auth_key_name)}",
        }        
        try:
            response = requests.post(self.api_conf.api_service + endpoint, headers=headers, json=data, timeout=self.api_conf.api_timeout_seconds)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"[FE->BE] GET error: {e}")
