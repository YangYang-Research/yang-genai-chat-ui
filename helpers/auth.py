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

jwt_secret_key = aws_secret_manager.get_secret(app_conf.app_jwt_key_name)

def create_jwt_cookie(jwt_token: str):
    cookie_manager.set(
        cookie='yang-cookie',
        val=jwt_token,
        path="/",
        key=jwt_secret_key,
        secure=True,
    )
        
def verify_jwt_token(jwt_token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(jwt_token, jwt_secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        st.warning("Session expired. Please log in again.")
        return None
    except jwt.InvalidTokenError as e:
        st.error("Invalid token. Please log in again.")
        return None
    
def clear_cookie():
    cookie_manager.delete('yang-cookie')

def get_logout():
    st.session_state["authentication_status"] = None
    clear_cookie()
    return True

def check_user_login(extend_key: str) -> bool:
    all_cookies = cookie_manager.get_all(key="cookie-" + extend_key)

    if 'yang-cookie' not in all_cookies:
        st.session_state["authentication_status"] = False
        return False

    jwt_cookie = all_cookies['yang-cookie']

    user_info = verify_jwt_token(jwt_cookie)

    if user_info:
        st.session_state["authentication_status"] = True
        return True

    st.session_state["authentication_status"] = False
    return False

def get_user_info(extend_key: str) -> Optional[Dict]:
    all_cookies = cookie_manager.get_all(key="cookie-" + extend_key)

    if 'yang-cookie' not in all_cookies:
        st.rerun()

    jwt_cookie = all_cookies['yang-cookie']

    user_info = verify_jwt_token(jwt_cookie)

    if user_info:
        return user_info
    
    session_user = st.session_state.get("userinfo")
    create_jwt_cookie(session_user)
    return session_user