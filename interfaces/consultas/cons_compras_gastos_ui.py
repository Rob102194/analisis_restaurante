import streamlit as st
import pandas as pd
from datetime import date
from utils.data_processing import procesar_dataframe_editado
from utils.validators import ValidadorRegistros
from utils.error_handler import ErrorHandler
from interfaces.base_ui import BaseEditableUI

class ConsultasComprasGastosUI(BaseEditableUI):
    def __init__(self, consultas_compras_gastos_logic):
        super().__init__()
        self.logic = consultas_compras_gastos_logic
        self._inicializar_estado()
    
    def _inicializar_estado(self):
        if 'consulta_actual' not in st.session_state:
            st.session_state.consulta_actual = {
                'datos_originales': [],
                'datos_editados': []
            }
    
    def mostrar_interfaz(self):
        st.header("🔍 Consulta de Registros")
        self._mostrar_filtros()
        self._mostrar_resultados()
    
    def _mostrar_filtros(self):
        with st.form("form_filtros"):
            cols = st.columns(2)
            fecha_inicio = cols[0].date_input("Fecha inicio", value=date.today())
            fecha_fin = cols[1].date_input("Fecha fin", value=date.today())
            
            categoria = st.selectbox("Categoría", ["Mercancía", "Equipos", "Limpieza", "Servicios", "Otros"])
            producto = st.text_input("Producto/Servicio (opcional)")
            
            if st.form_submit_button("🔎 Buscar"):
                filtros = {
                    "fecha_inicio": fecha_inicio.isoformat(),
                    "fecha_fin": fecha_fin.isoformat(),
                    "categoria": categoria.lower(),
                    "producto": producto.strip()
                }
                
                resultados = self.logic.consultar_registros(filtros)
                st.session_state.consulta_actual = {
                    'datos_originales': resultados,
                    'datos_editados': resultados.copy()
                }
    
    def _mostrar_resultados(self):
        if st.session_state.consulta_actual['datos_originales']:
            df = pd.DataFrame(st.session_state.consulta_actual['datos_editados'])
            
            if not df.empty and 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'])
                
                df["cantidad"] = df.apply(
                    lambda x: x["cantidad"] if x["categoria"] == "mercancía" else None, 
                    axis=1
                )
                df["unidad_medida"] = df.apply(
                    lambda x: x["unidad_medida"] if x["categoria"] == "mercancía" else None, 
                    axis=1
                )

            edited_df = self._create_data_editor(df, "consulta")

            # Actualizar registros inmediatamente
            try:
                edited_data = procesar_dataframe_editado(edited_df)
            except ValueError as e:
                st.error(f"Error de formato: {str(e)}")
                st.stop()
            
            if not edited_df.equals(df):    
                st.session_state.consulta_actual['datos_editados'] = edited_data
                st.rerun()

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Confirmar cambios", type="primary"):
                    self.confirmar_registros()
            with col2:
                if st.button("↩️ Deshacer cambios"):
                    self._restaurar_datos_originales()
            with col3:
                if st.button("🗑️ Nueva búsqueda"):
                    self._reiniciar_busqueda()

    def confirmar_registros(self):
        registros_invalidos = []
        cambios_pendientes = []
        eliminaciones_procesadas = []
        
        # Obtener datos originales y editados
        datos_editados = [
            reg for reg in st.session_state.consulta_actual['datos_editados']
            if reg is not None and isinstance(reg, dict) and reg.get('id')
        ]
        datos_originales = st.session_state.consulta_actual['datos_originales']
        originales_por_id = {reg['id']: reg for reg in datos_originales}
        
        ids_originales = {reg['id'] for reg in datos_originales} if datos_originales else set()
        ids_editados = {reg['id'] for reg in datos_editados} if datos_editados else set()

        if not datos_editados and datos_originales:
            eliminaciones_pendientes_ids = ids_originales
        else:
            eliminaciones_pendientes_ids = list(ids_originales - ids_editados)

        
        # Procesar actualizaciones
        for reg_id in eliminaciones_pendientes_ids:
            try:
                reg_original = next(
                    (r for r in datos_originales if r['id'] == reg_id),
                    None
                )
                if reg_original:
                    tabla = "compras" if reg_original["categoria"] == "mercancía" else "gastos"
                    eliminaciones_procesadas.append({
                        'tabla': tabla,
                        'id': reg_id
                    })
            except Exception as e:
                registros_invalidos.append(f"Error eliminando registro {reg_id}: {str(e)}")

        for reg_editado in datos_editados:
            try:
                reg_id = int(reg_editado.get('id'))
                reg_original = originales_por_id.get(reg_id)

                # Validación básica
                if not reg_original:
                    raise ValueError("Registro original no encontrado")

                # Validar campos comunes
                errores = ValidadorRegistros.validar_campos_comunes(reg_editado)
                if errores:
                    raise ValueError("\n".join(errores))

                # Filtrar campos no permitidos
                reg_limpio = ValidadorRegistros.filtrar_campos(reg_editado.copy())
                
                # Detectar cambios
                cambios = self._detectar_cambios(reg_original, reg_editado, reg_limpio)
                if cambios:
                    tabla = ValidadorRegistros.obtener_tabla(reg_limpio)
                    cambios_pendientes.append({
                        'tabla': tabla,
                        'id': reg_id,
                        'datos': cambios
                    })

            except Exception as e:
                registros_invalidos.append(f"Registro {reg_id}: {str(e)}")

        if registros_invalidos:
            ErrorHandler.display_validation_errors(registros_invalidos, "consulta")
            st.stop()

        # Actualizar registros modificados
        for cambio in cambios_pendientes:
            self.logic.data_service.db.execute_safe_operation(
                operation='update',
                table=cambio['tabla'],
                record_id=cambio['id'],
                data=cambio['datos']
            )

        # Eliminar registros marcados
        if eliminaciones_procesadas:
            for eliminacion in eliminaciones_procesadas:
                self.logic.data_service.db.execute_safe_operation(
                    operation='delete',
                    table=eliminacion['tabla'],
                    record_id=eliminacion['id']
                )
            st.success("**¡Registros eliminados exitosamente!** ✅")
            self._reiniciar_busqueda()
        else:
            st.warning("No hay cambios para guardar")

        # Actualizar estado y notificar
        st.session_state.consulta_actual['datos_originales'] = datos_editados.copy()
        st.success("**¡Operaciones completadas exitosamente!** ✅")
        self._reiniciar_busqueda()
        
    def _detectar_cambios(self, original, editado, reg_limpio):
        cambios = {}
        campos_relevantes = ['fecha', 'categoria', 'producto', 'monto', 'cantidad', 'unidad_medida']
        
        for campo in campos_relevantes:
            if campo not in reg_limpio:
                continue
                
            v_editado = editado.get(campo)
            v_original = original.get(campo)
            
            # Normalizar fechas
            if campo == "fecha":
                v_editado = pd.to_datetime(v_editado).isoformat() if v_editado else None
                v_original = pd.to_datetime(v_original).isoformat() if v_original else None
            
            # Comparación estricta
            if v_editado != v_original:
                cambios[campo] = v_editado
        
        return cambios
    
    def _restaurar_datos_originales(self):
        """Restaura los datos a su estado original antes de las ediciones"""
        st.session_state.consulta_actual['datos_editados'] = st.session_state.consulta_actual['datos_originales'].copy()
        st.rerun()

    def _reiniciar_busqueda(self):
        """Elimina completamente los resultados y prepara para nueva búsqueda"""
        keys_to_remove = ['consulta_actual']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    def _actualizar_registro(self, datos):
        tabla = "compras" if datos["categoria"] == "mercancía" else "gastos"
        self.logic.db.client.table(tabla).update(datos).eq("id", datos["id"]).execute()

    