from utils.validators import ValidadorRegistros
import streamlit as st

class ErrorHandler:
    @staticmethod
    def handle_db_error(error, context):
        error_template = """
        **Error en {context}**  
        Detalles: `{error}`  
        """
        return st.error(error_template.format(context=context, error=str(error)))

    @staticmethod
    def display_validation_errors(errors, context):
        st.error(ValidadorRegistros.construir_mensaje_error(errors, context))