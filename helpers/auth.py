import streamlit as st
import jwt
from typing import Optional, Dict
import extra_streamlit_components as stx
from helpers.config import AppConfig, AWSConfig
from helpers.secret import AWSSecretManager

app_conf = AppConfig()
aws_conf = AWSConfig()
aws_secret_manager = AWSSecretManager()
cookie_manager = stx.CookieManager()

jwt_secret_key = aws_secret_manager.get_secret(app_conf.jwt_key_name)

def verify_jwt_cookie(jwt_cookie: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(jwt_cookie, jwt_secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        st.warning("Session expired. Please log in again.")
        return None
    except jwt.InvalidTokenError as e:
        st.error("Invalid token. Please log in again.")
        return None
    
def clear_jwt_cookie(cookie_name: str):
    cookie_manager.delete(cookie_name)

def get_logout():
    st.session_state["authentication_status"] = None
    clear_jwt_cookie("cell")

def get_user_info(extend_key: str) -> Optional[Dict]:
    all_cookies = cookie_manager.get_all(key="cookie-"+extend_key)

    if 'cell' in all_cookies:
        jwt_cookie = all_cookies['cell']
    
    if st.session_state.get("authentication_status"):
        user_info = st.session_state.get("username")
        if not user_info:
            user_info = verify_jwt_cookie(jwt_cookie)
        return user_info
    elif jwt_cookie:
        user_info = verify_jwt_cookie(jwt_cookie)
        if user_info:
            return user_info
    else:
        clear_jwt_cookie("cell")
        return None