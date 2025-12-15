import streamlit as st
from helpers.loog import logger
from helpers.config import APIConfig
from helpers.http import MakeRequest
import pandas as pd

class UserPage:
    def __init__(self):
        self.api_conf = APIConfig()
        self.make_request = MakeRequest()

    def display(self):
        st.title("User Management")
        st.caption("Manage the users of the system.", help="Users are the individuals who can access the system and perform actions.")
        
        # Fetch roles and build a map from id to name
        roles_resp_json, _ = self.make_request.get(endpoint=self.api_conf.role_endpoint)
        roles_sorted = sorted(roles_resp_json, key=lambda x: x["id"])
        roles_display_names = [role["name"] for role in roles_sorted]
        role_id_to_name = {role["id"]: role["name"] for role in roles_sorted}

        # Fetch users and map role_id -> role_name
        users_resp_json, _ = self.make_request.get(endpoint=self.api_conf.user_endpoint)
        users_sorted = sorted(users_resp_json, key=lambda x: x["username"].lower())
        # Map role_id to name for display
        users_for_df = []
        for user in users_sorted:
            user_copy = user.copy()
            if "role_id" in user_copy and user_copy["role_id"] in role_id_to_name:
                user_copy["role_id"] = role_id_to_name[user_copy["role_id"]]
            users_for_df.append(user_copy)
        
        users_df = pd.DataFrame(users_for_df, columns=["id", "username", "email", "fullname", "changed_password", "role_id", "active_status"])
        users_df = users_df.rename(columns={"id": "ID", "username": "Username", "email": "Email", "fullname": "Full Name", "changed_password": "Changed Password", "role_id": "Role", "active_status": "Active Status"})
        dataframe = st.dataframe(
            users_df,
            column_order=list(users_df.columns),
            key="users_dataframe",
            on_select="rerun",
            selection_mode="single-cell",
            width="stretch",
            hide_index=True,
        )
        tab1, tab2, tab3 = st.tabs(["Create User", "Update User", "Delete User"])

        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                input_username = st.text_input("Username:", key=f"username_create", help="The username of the user.")
                input_email = st.text_input("Email:", key=f"email_create", help="The email of the user.")
                input_fullname = st.text_input("Full Name:", key=f"fullname_create", help="The full name of the user.")
                input_password = st.text_input("Password:", key=f"password_create", help="The password of the user.", type="password")
                input_role_id = st.selectbox("Select Role:", options=roles_display_names, key=f"role_id_create", help="The role of the user.")
                input_active_status = st.selectbox("Select Active Status:", options=["enable", "disable"], index=0, key=f"active_status_create", help="The active status of the user.")
                if st.button("Create", key=f"create_user"):
                    payload = {
                        "username": input_username,
                        "email": input_email,
                        "fullname": input_fullname,
                        "hashed_password": input_password,
                        "changed_password": False,
                        "role_id": roles_sorted[roles_display_names.index(input_role_id)]["id"],
                        "active_status": input_active_status,
                        "trashed": False,
                    }
                    resp_json, status_code = self.make_request.post(endpoint=self.api_conf.user_endpoint, data=payload)
                    if status_code == 201:
                        st.success("User created successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to create user. Traceback: " + resp_json.get("detail"))
                        st.rerun()

        with tab2:
            col1, col2, col3 = st.columns(3)
            with col1:
                header = st.empty()
                header.caption("Select user in the table to update.")
                selected_cells = dataframe.selection.cells
                if selected_cells:
                    header.empty()
                    row_index, col_name = selected_cells[0]
                    row_data = users_df.iloc[row_index].to_dict()
                    input_username = st.text_input(
                        "Username:",
                        key=f"username_update_{row_data['ID']}",
                        value=row_data['Username'],
                        help="The username of the user.",
                    )
                    input_email = st.text_input(
                        "Email:",
                        key=f"email_update_{row_data['ID']}",
                        value=row_data['Email'],
                        help="The email of the user."
                    )
                    input_fullname = st.text_input(
                        "Full Name:",
                        key=f"fullname_update_{row_data['ID']}",
                        value=row_data['Full Name'],
                        help="The full name of the user."
                    )
                    input_role_id = st.selectbox(
                        "Select Role:",
                        options=roles_display_names,
                        index=roles_display_names.index(row_data['Role']) if row_data['Role'] in roles_display_names else 0,
                        key=f"role_id_update_{row_data['ID']}",
                        help="The role of the user."
                    )
                    input_active_status = st.selectbox(
                        "Select Active Status:",
                        options=["enable", "disable"],
                        index=0 if row_data['Active Status'] == "enable" else 1,
                        key=f"active_status_update_{row_data['ID']}",
                        help="The active status of the user."
                    )
                    if st.button("Update", key=f"update_user_{row_data['ID']}"):
                        payload = {
                            "username": input_username,
                            "email": input_email,
                            "fullname": input_fullname,
                            "role_id": roles_sorted[roles_display_names.index(input_role_id)]["id"],
                            "active_status": input_active_status,
                            "trashed": False,
                        }
                        resp_json, status_code = self.make_request.put(endpoint=self.api_conf.user_endpoint + str(row_data['ID']), data=payload)
                        if status_code == 200:
                            st.success("User updated successfully.")
                            st.rerun()
                        else:
                            st.error("Failed to update user. Traceback: " + resp_json.get("detail"))
                            st.rerun()

        with tab3:
            col1, col2, col3 = st.columns(3)
            with col1:
                header = st.empty()
                header.caption("Select user in the table to delete.")
                selected_cells = dataframe.selection.cells
                if selected_cells:
                    header.empty()
                    row_index, col_name = selected_cells[0]
                    row_data = users_df.iloc[row_index].to_dict()
                    st.warning(f"Are you sure you want to delete user: **{row_data['Username']}**?")
                    if st.button("Delete", key=f"delete_user_{row_data['ID']}"):
                        resp_json, status_code = self.make_request.delete(endpoint=self.api_conf.user_endpoint + str(row_data['ID']))
                        if status_code == 204:
                            st.success("User deleted successfully.")
                            st.rerun()
                        else:
                            st.error("Failed to delete user. Traceback: " + resp_json.get("detail"))
                            st.rerun()
    def run(self):
        self.display()

def main():
    try:
        page = UserPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()