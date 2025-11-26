import streamlit as st
from helpers.loog import logger
from helpers.auth import get_logout

class LogoutPage:
    def __init__(self):
        pass

    def display(self):
        get_logout()
        st.success("You have been logged out successfully.")
        st.rerun()
        
    def run(self):
        self.display()

def main():
    try:
        page = LogoutPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()