import streamlit as st
from datetime import datetime
from auth.auth import login_form
from modules.database import DatabaseManager
from interfaces.sidebar import SidebarManager
from modules.logic.regist_compras_gastos_logic import RegistroManager
from interfaces.registro.regist_comp_gast_ui import RegistroUI
from modules.logic.cons_compras_gastos_logic import ConsultasComprasGastosLogic
from interfaces.consultas.cons_compras_gastos_ui import ConsultasComprasGastosUI
from utils.data_service import DataService
# ======================
#  CONFIGURACIÓN INICIAL
# ======================
def configuracion_inicial():
    """Configura los parámetros iniciales de la aplicación"""
    st.set_page_config(
        page_title="Gestión de Restaurante",
        page_icon="🍽️",
        layout="wide",
        menu_items={
            'Get Help': 'https://ejemplo.com/soporte',
            'Report a bug': 'https://ejemplo.com/bugs',
        }
    )

# ======================
#  MANEJO AUTENTICACIÓN
# ======================
def manejar_autenticacion():
    """Controla el flujo de autenticación del usuario"""
    if 'user' not in st.session_state:
        st.session_state.update({
            'user': None,
            'authenticated': False,
            'last_login': datetime.now()
        })
    
    if not st.session_state.authenticated:
        with st.spinner("Verificando credenciales..."):
            if not login_form():
                st.stop()

# ======================
#  INICIALIZACIÓN RECURSOS
# ======================
@st.cache_resource
def inicializar_componentes():
    if 'registros_temporales' not in st.session_state:
        st.session_state.registros_temporales = []
    
    # Crear la instancia única de DatabaseManager
    db = DatabaseManager()

    # Crear servicio de datos
    data_service = DataService(db)

    return {
        'data_service': data_service,
        'registro_manager': RegistroManager(data_service),
        'consultas_compras_gastos_logic': ConsultasComprasGastosLogic(data_service)
    }

# ======================
#  FUNCIONES AUXILIARES
# ======================
def mostrar_debug_info(consultas_logic):
    """Muestra información de depuración en la sidebar"""
    if st.checkbox("🐞 Modo Debug", key="debug_final"):
        st.write("### Estado Actual:")
        st.write("Última Query:", consultas_logic.last_query)

def mostrar_footer():
    """Muestra el pie de página en la sidebar"""
    st.sidebar.markdown(f"""
    **Usuario:** {st.session_state.user}  
    **Última conexión:** {st.session_state.last_login.strftime("%d/%m/%Y %H:%M")}
    """)

# ======================
#  VISTAS PRINCIPALES
# ======================

#def mostrar_pagina_consultas():
#    """Muestra el módulo de consultas con pestañas"""
#    tab_ventas, tab_gastos = st.tabs(["💰 Ventas", "📉 Gastos"])
#    
#    with tab_ventas:
#        VentasUI(ConsultasLogic(DatabaseManager())).mostrar_consulta_completa()
        
#    with tab_gastos:
#        GastosUI(ConsultasLogic(DatabaseManager())).mostrar_consulta_completa()

def mostrar_pagina_analisis():
    """Muestra el dashboard analítico"""
    st.header("📊 Dashboard Analítico")
    with st.spinner("Cargando análisis..."):
        # Lógica de análisis aquí
        st.info("Módulo en desarrollo")

# ======================
#  FUNCIÓN PRINCIPAL
# ======================
def main():
    # Configuración inicial
    configuracion_inicial()
    manejar_autenticacion()
    
    # Inicialización de componentes
    componentes = inicializar_componentes()
    sidebar = SidebarManager()

    registro_ui = RegistroUI(componentes['registro_manager'])
    consultas_compras_gastos_ui = ConsultasComprasGastosUI(componentes['consultas_compras_gastos_logic'])

    # Elementos de la sidebar
    #with st.sidebar:
        #mostrar_debug_info(componentes['consultas_logic'])
        #mostrar_footer()
    
    # Sistema de routing
    opciones_menu = {
        "Registro": lambda: registro_ui.mostrar_interfaz(),
        "Consulta": lambda: consultas_compras_gastos_ui.mostrar_interfaz()
        #"Análisis": mostrar_pagina_analisis
    }
    
    # Ejecutar vista seleccionada
    opcion_seleccionada = sidebar.menu_option
    opciones_menu.get(opcion_seleccionada, lambda: st.error("Opción no válida"))()

# ======================
#  EJECUCIÓN PRINCIPAL
# ======================
if __name__ == "__main__":
    main()