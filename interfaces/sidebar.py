import streamlit as st
from streamlit_option_menu import option_menu
import os

class SidebarManager:
    def __init__(self):
        self._render()
        
    def _render(self):
        self.menu_config = {
            "options": ["Registro", "Consulta", "Análisis"],
            "icons": ["cloud-upload", "search", "bar-chart"],
            "styles": {
                "container": {"padding": "0!important"},
                "nav-link": {"font-size": "16px"}
            }
        }
        self._render_sidebar()

    def _render_logo(self):
        """Renderiza el logo en la sidebar"""
        ruta_logo = os.path.abspath("assets/logo.png")
        st.image(ruta_logo, width=120)
        st.markdown("---")

    def _render_menu(self) -> None:
        """Renderiza el menú de navegación"""
        self.selected_option = option_menu(
            menu_title=None,
            options=self.menu_config["options"],
            icons=self.menu_config["icons"],
            default_index=0,
            styles=self.menu_config["styles"]
        )

    def _render_logout(self) -> None:
        """Renderiza el botón de logout"""
        if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    def _render_sidebar(self) -> None:
        """Construye toda la barra lateral"""
        with st.sidebar:
            self._render_logo() 
            self._render_menu()
            st.markdown("---")
            self._render_logout()

    @property
    def menu_option(self) -> str:
        """Devuelve la opción seleccionada del menú"""
        return self.selected_option