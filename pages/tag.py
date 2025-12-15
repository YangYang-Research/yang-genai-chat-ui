import streamlit as st
import pandas as pd
from helpers.loog import logger
from helpers.config import APIConfig
from helpers.http import MakeRequest

class TagPage:
    def __init__(self):
        self.api_conf = APIConfig()
        self.make_request = MakeRequest()

    def display(self):
        st.title("Tags")
        st.caption(
            "Configure the tags available for your AI assistant.",
            help="Tags allow your AI assistant to categorize and filter its responses."
        )
        resp_json = self.make_request.get(endpoint=self.api_conf.tag_endpoint)
        tags_sorted = sorted(resp_json, key=lambda x: x["id"])

        if tags_sorted:
            tags_df = pd.DataFrame(tags_sorted, columns=["id", "tag", "status"])
            tags_df = tags_df.rename(columns={"id": "ID", "tag": "Tag", "status": "Status"})
            dataframe = st.dataframe(
                tags_df,
                column_order=list(tags_df.columns),
                key="tags_dataframe",
                on_select="rerun",
                selection_mode="single-cell",
                width="stretch",
                hide_index=True,
            )
            tab1, tab2, tab3 = st.tabs(["Create Tag", "Update Tag", "Delete Tag"])
            with tab1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    input_tag = st.text_input("Tag:", key=f"tag_create", help="The tag.")
                    input_status = st.selectbox("Select Status:", 
                        options=["enable", "disable"],
                        index=0,
                        key=f"status_create", 
                        help="The status to create the tag with."
                    )
                    if st.button("Create", key=f"create_tag"):
                        payload = {
                            "tag": input_tag,
                            "status": input_status,
                            "trashed": False,
                        }
                        resp_json = self.make_request.post(endpoint=self.api_conf.tag_endpoint, data=payload)
                        st.success("Tag created successfully.")
                        st.rerun()
            with tab2:
                header = st.empty()
                header.caption("Select tag in the table to update.")
                selected_cells = dataframe.selection.cells
                if selected_cells:
                    header.empty()
                    row_index, col_name = selected_cells[0]
                    row_data = tags_df.iloc[row_index].to_dict()
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        input_tag = st.text_input("Tag:", key=f"tag_{row_data['ID']}", value=row_data['Tag'], help="The tag.")
                        input_status = st.selectbox("Select Status:", 
                            options=["enable", "disable"],
                            index=0 if row_data['Status'] == "enable" else 1,
                            key=f"status_{row_data['ID']}", 
                            help="The status to change the tag to."
                        )
                        if st.button("Update", key=f"update_tag_{row_data['ID']}"):
                            payload = {
                                "tag": input_tag,
                                "status": input_status,
                                "trashed": False,
                            }
                            resp_json = self.make_request.put(endpoint=self.api_conf.tag_endpoint + str(row_data['ID']), data=payload)
                            st.success("Tag status updated successfully.")
                            st.rerun()
            with tab3:
                header = st.empty()
                header.caption("Select tag in the table to delete.")
                selected_cells = dataframe.selection.cells
                if selected_cells:
                    header.empty()
                    row_index, col_name = selected_cells[0]
                    row_data = tags_df.iloc[row_index].to_dict()
                    st.warning(f"Are you sure you want to delete tag: **{row_data['Tag']}**?")
                    if st.button("Delete", key=f"delete_tag_{row_data['ID']}"):
                        resp_json = self.make_request.delete(endpoint=self.api_conf.tag_endpoint + str(row_data['ID']))
                        st.success("Tag deleted successfully.")
                        st.rerun()
        else:
            st.info("No tags found.")

    def run(self):
        self.display()

def main():
    try:
        page = TagPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()