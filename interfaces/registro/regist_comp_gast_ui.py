import streamlit as st
import pandas as pd
from datetime import datetime
from interfaces.base_ui import BaseEditableUI
from utils.data_processing import procesar_dataframe_editado
from utils.error_handler import ErrorHandler

class RegistroUI(BaseEditableUI):
    def __init__(self, registro_manager):
        super().__init__()
        self.manager = registro_manager
        self._inicializar_estado()
        
    def _inicializar_estado(self):
        if 'registros_temporales' not in st.session_state:
            st.session_state.registros_temporales = []
        
    def mostrar_interfaz(self):
        st.header("📥 Registro de Compras y Gastos")
        self._mostrar_formulario()
        self._mostrar_tabla_editable()

    def _mostrar_formulario(self):
        with st.form("form_compras_gastos"):
             self._render_campos_formulario()
            
    def _render_campos_formulario(self):        
        cols = st.columns(2)
        fecha = cols[0].date_input("Fecha", value=datetime.today())
        categoria = cols[1].selectbox("Categoría", ["Mercancía", "Equipos", "Nomina", "Servicios", "Otros"])
        
        producto = st.text_input("Producto/Servicio", max_chars=100)
        
        cols_mercancia = st.columns(2)
        cantidad = cols_mercancia[0].number_input("Cantidad", min_value=0.0, format="%.3f", help="Requerido para Mercancía")
        unidad = cols_mercancia[1].selectbox("Unidad", ["unidad", "kg", "litros", "paquete"], help="Requerido para Mercancía")

        monto = st.number_input("Monto ($)", min_value=0.0, format="%.2f")
        proveedor = st.text_input("Proveedor (opcional)", max_chars=100) or None
        descripcion = st.text_area("Descripción adicional (opcional)") or None
        
        if st.form_submit_button("➕ Agregar a lista temporal"):
            registro = {
                'fecha': fecha.isoformat(), 
                'categoria': categoria.lower(),
                'producto': producto,
                'monto': monto,
                'cantidad': cantidad,
                'unidad_medida': unidad,
                'proveedor': proveedor,
                'descripcion': descripcion
            }
                    
            success, msg = self.manager.agregar_registro_temporal(registro)

            if not success:
                st.toast("⚠️ Error al agregar registro")
                ErrorHandler.display_validation_errors(
                    errors=str(msg).split("\n"),
                    context="formulario"
                )
            else:
                st.toast(msg)

    def _mostrar_tabla_editable(self):
        if st.session_state.registros_temporales:
            st.subheader("📋 Registros a confirmar")

            # Convertir a DataFrame y manejar fechas
            df = pd.DataFrame(st.session_state.registros_temporales)

            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'])

            # Configurar columnas editables
            edited_df = self._create_data_editor(df, "registro")
            
            # Actualizar registros temporales inmediatamente
            try:
                edited_data = procesar_dataframe_editado(edited_df)
            except ValueError as e:
                st.error(f"Error de formato: {str(e)}")
                st.stop()
            
            if not edited_df.equals(df):
                st.session_state.registros_temporales = edited_data
                st.rerun()  # Forzar actualización
            
        # Botón de confirmación
        if st.button("✅ Confirmar todos", type="primary"):
            if not st.session_state.registros_temporales:
                st.error("📭 **Tabla vacía:** Agrega registros antes de confirmar")
            else:
                try:
                    self.manager.confirmar_registros()
                    st.success("**¡Datos guardados!** ✅")
                    st.balloons()
                    st.session_state.registros_temporales = []
                    st.rerun()
                    
                except RuntimeError as e:
                    with st.container(border=True):
                        st.markdown(str(e))
                        
                except Exception as e:
                    st.error(f"""
                    **Error inesperado:**  
                    ```python
                    {str(e)}
                    ```  
                    Contacta al soporte técnico 🔧
                    """)