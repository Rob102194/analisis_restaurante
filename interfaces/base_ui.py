import streamlit as st
from interfaces.ui_componentes.column_configs import ColumnConfigFactory

class BaseEditableUI:
    def __init__(self):
        self.column_configs = ColumnConfigFactory()
    
    def _create_data_editor(self, df, key_suffix=""):
        config = self.column_configs.get_column_configs()

        return st.data_editor(
            df,
            column_config=config,
            num_rows="dynamic",
            key=f"editor_{key_suffix}",
            hide_index=True
        )