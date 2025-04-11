import streamlit as st
from datetime import datetime

class TablaEditable:
    @staticmethod
    def _get_column_config(self, df):
        column_config = {
                "fecha": st.column_config.DateColumn(
                    "Fecha",
                    format="YYYY-MM-DD",
                    default=datetime.today().date()
                ),
                "categoria": st.column_config.SelectboxColumn(
                    "Categoría", 
                    options=["mercancía", "equipos", "limpieza", "servicios", "otros"]
                ),
                "unidad_medida": st.column_config.SelectboxColumn(
                    "Unidad", 
                    options=["unidad", "kg", "litros", "paquete"],
                    required=False
                ) if 'unidad_medida' in df.columns else None,
                "cantidad": st.column_config.NumberColumn(
                    "Cantidad",
                    format="%.3f",
                    required=False
                ) if 'cantidad' in df.columns else None
            }
        return {k: v for k, v in column_config.items() if v is not None}