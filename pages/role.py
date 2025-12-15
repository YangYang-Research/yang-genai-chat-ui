import streamlit as st
from helpers.loog import logger
from helpers.config import APIConfig
from helpers.http import MakeRequest
import pandas as pd

class RolePage:
    def __init__(self):
        self.api_conf = APIConfig()
        self.make_request = MakeRequest()

    def display(self):
        st.title("Role Management")
        st.caption("Manage the roles of the system.", help="Roles are the permissions that users can have in the system.")
        roles_resp_json, _ = self.make_request.get(endpoint=self.api_conf.role_endpoint)
        roles_sorted = sorted(roles_resp_json, key=lambda x: x["id"])
        if roles_sorted:
            roles_df = pd.DataFrame(roles_sorted, columns=["id", "name", "description", "status"])
            roles_df = roles_df.rename(columns={"id": "ID", "name": "Name", "description": "Description", "status": "Status"})
            dataframe = st.dataframe(
                roles_df,
                column_order=list(roles_df.columns),
                key="roles_dataframe",
                on_select="rerun",
                selection_mode="single-cell",
                width="stretch",
                hide_index=True,
            )
            tab1, tab2, tab3 = st.tabs(["Create Role", "Update Role", "Delete Role"])
            with tab1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    input_name = st.text_input("Name:", key=f"name_create", help="The name of the role.")
                    input_description = st.text_area("Description:", key=f"description_create", help="The description of the role.")
                    input_status = st.selectbox("Select Status:", 
                        options=["enable", "disable"],
                        index=0,
                        key=f"status_create", 
                        help="The status to create the role with."
                    )
                    if st.button("Create", key=f"create_role"):
                        payload = {
                            "name": input_name,
                            "description": input_description,
                            "status": input_status,
                            "trashed": False,
                        }
                        resp_json, status_code = self.make_request.post(endpoint=self.api_conf.role_endpoint, data=payload)
                        if status_code == 201:
                            st.success("Role created successfully.")
                            st.rerun()
                        else:
                            st.error("Failed to create role. Traceback: " + resp_json.get("detail"))
                            st.rerun()
            with tab2:
                header = st.empty()
                header.caption("Select role in the table to update.")
                selected_cells = dataframe.selection.cells
                if selected_cells:
                    header.empty()
                    row_index, col_name = selected_cells[0]
                    row_data = roles_df.iloc[row_index].to_dict()
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        input_name = st.text_input("Name:", key=f"role_name_{row_data['ID']}", value=row_data['Name'], help="The name of the role.", disabled=True)
                        input_description = st.text_area("Description:", key=f"role_description_{row_data['ID']}", value=row_data['Description'], help="The description of the role.")
                        input_status = st.selectbox("Select Status:", 
                            options=["enable", "disable"],
                            index=0 if row_data['Status'] == "enable" else 1,
                            key=f"role_status_{row_data['ID']}", 
                            help="The status to update the role to."
                        )
                    if st.button("Update", key=f"update_role_{row_data['ID']}"):
                        payload = {
                            "name": input_name,
                            "description": input_description,
                            "status": input_status,
                            "trashed": False,
                        }
                        resp_json, status_code = self.make_request.put(endpoint=self.api_conf.role_endpoint + str(row_data['ID']), data=payload)
                        if status_code == 200:
                            st.success("Role updated successfully.")
                            st.rerun()
                        else:
                            st.error("Failed to update role. Traceback: " + resp_json.get("detail"))
                            st.rerun()
            with tab3:
                header = st.empty()
                header.caption("Select role in the table to delete.")
                selected_cells = dataframe.selection.cells
                if selected_cells:
                    header.empty()
                    row_index, col_name = selected_cells[0]
                    row_data = roles_df.iloc[row_index].to_dict()
                    st.warning(f"Are you sure you want to delete role: **{row_data['Name']}**?")
                    if st.button("Delete", key=f"delete_role_{row_data['ID']}"):
                        resp_json, status_code = self.make_request.delete(endpoint=self.api_conf.role_endpoint + str(row_data['ID']))
                        if status_code == 204:
                            st.success("Role deleted successfully.")
                            st.rerun()
                        else:
                            st.error("Failed to delete role. Traceback: " + resp_json.get("detail"))
                            st.rerun()
        else:
            st.info("No roles found.")

    def run(self):
        self.display()

def main():
    try:
        page = RolePage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()