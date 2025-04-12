import streamlit as st
from datetime import datetime, date
from utils.validators import ValidadorRegistros
from utils.error_handler import ErrorHandler

class RegistroManager:
    def __init__(self, data_service):
        self.data_service = data_service
        self._inicializar_registros_temporales()

    def _inicializar_registros_temporales(self):
        if 'registros_temporales' not in st.session_state:
            st.session_state.registros_temporales = []

    def agregar_registro_temporal(self, datos_raw):
        """Valida y estructura los datos antes de almacenarlos"""
        try:
            # Forzar eliminación de campos innecesarios
            if datos_raw.get('categoria') != 'mercancía':
                datos_raw.pop('cantidad', None)
                datos_raw.pop('unidad_medida', None)

            datos = self._construir_datos(datos_raw)
            st.session_state.registros_temporales.append(datos)
            return True, "✅ Registro temporal agregado"
        except (KeyError, ValueError) as e:
            return False, f"❌ Error: {str(e)}"

    def _construir_datos(self, datos_raw):
        campos_obligatorios = ['fecha', 'categoria', 'producto', 'monto']
        for campo in campos_obligatorios:
            if not datos_raw.get(campo):
                raise ValueError(f"Campo obligatorio faltante: {campo}")
        
        if not str(datos_raw['producto']).strip():
            raise ValueError("📌 Producto no puede estar vacío")
        
        if datos_raw.get('monto') is None:
            raise ValueError("El campo 'monto' no puede estar vacío")  # <-- Nueva línea
        
        monto = float(datos_raw['monto'])
        if not monto or monto <= 0:
            raise ValueError("💰 Monto debe ser > 0")
       
        # Validación obligatoria para mercancía
        if datos_raw['categoria'] == 'mercancía':
            if datos_raw.get('cantidad') is None:
                raise ValueError("Cantidad es obligatoria para mercancía")
            if datos_raw.get('unidad_medida') is None:
                raise ValueError("Unidad de medida es obligatoria para mercancía")
        
        # Construcción de datos
        datos = {
            'fecha': self._normalizar_fecha(datos_raw['fecha']),
            'categoria': datos_raw['categoria'].lower().strip(),
            'producto': datos_raw['producto'].strip(),
            'monto': float(datos_raw['monto']),
            'cantidad': float(datos_raw['cantidad']),
            'unidad_medida': datos_raw.get('unidad_medida'),
            'proveedor': datos_raw.get('proveedor'),
            'descripcion': datos_raw.get('descripcion')
        }
        
        if datos['categoria'] != 'mercancía':
            datos.pop('cantidad', None) 
            datos.pop('unidad_medida', None)

        return datos

    def _normalizar_fecha(self, fecha):
        """Convierte diferentes formatos de fecha a ISO"""
        if isinstance(fecha, (date, datetime)):
            return fecha.isoformat()
        try:
            return datetime.strptime(fecha, "%Y-%m-%d").date().isoformat()
        except:
            raise ValueError("Formato de fecha inválido")

    def eliminar_registros(self, indices):
        """Elimina registros por índices reales (no de la tabla paginada)"""
        nuevos_registros = [
            reg for idx, reg in enumerate(st.session_state.registros_temporales)
            if idx not in indices
        ]
        st.session_state.registros_temporales = nuevos_registros

    def confirmar_registros(self):
        registros_invalidos = []
        registros_procesados = []

        for idx, reg in enumerate(st.session_state.registros_temporales, start=1):
            try:
                reg = reg.copy()  # Evitar modificar el original

                # Validación común
                errores = ValidadorRegistros.validar_campos_comunes(reg)
                if errores:
                    raise ValueError("\n".join(errores))

                # Filtrar campos no permitidos
                reg_limpio = ValidadorRegistros.filtrar_campos(reg.copy())
                
                if not reg_limpio.get('monto') or not reg_limpio.get('producto'):
                    raise ValueError("Campos clave faltantes después de edición")
            
                # Determinar tabla
                tabla = ValidadorRegistros.obtener_tabla(reg_limpio)
                registros_procesados.append((tabla, reg_limpio))
                
            except Exception as e:
                registros_invalidos.append(f"Fila {idx}: {str(e)}")
        
        # Manejo de errores
        if registros_invalidos:
            ErrorHandler.display_validation_errors(registros_invalidos, "registro")
            st.stop()
        
        # Insertar en DB
        for tabla, datos in registros_procesados:
            tipo = "mercancía" if tabla == "compras" else "gastos"
            self.data_service.guardar_registro(tipo, datos)
        
        st.session_state.registros_temporales = []