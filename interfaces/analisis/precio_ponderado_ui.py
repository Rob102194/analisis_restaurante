import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class PrecioPonderadoUI:
    def __init__(self, logic):
        self.logic = logic
    
    def mostrar_interfaz(self):
        st.title("📈 Análisis de Precio Ponderado")
        
        # Obtener productos únicos
        productos = self.logic.obtener_productos()
        producto_seleccionado = st.selectbox("Seleccionar Producto", productos)
        
        # Selector de rango de fechas
        rango = st.selectbox("Período", [
            "Últimos 30 días", 
            "Últimos 60 días",
            "Últimos 90 días",
            "Este mes",
            "Últimos 6 meses",
            "Este año", 
            "Personalizado"]
        )
        
        fecha_inicio, fecha_fin = self._calcular_fechas(rango)
        
        # Obtener datos
        df = self.logic.obtener_precios_historicos(producto_seleccionado, fecha_inicio, fecha_fin)
        
        if not df.empty:
            # Precio ponderado
            precio_pond = self.logic.calcular_precio_ponderado(df)
            st.metric("Precio Ponderado del Período", f"${precio_pond:,.2f}")
            
            # Gráfico de precios
            fig = px.line(df, x='fecha', y='precio_unitario', title=f"Precio Unitario - {producto_seleccionado}")
            st.plotly_chart(fig)
            
        else:
            st.warning("No hay datos para el período seleccionado")
    
    def _calcular_fechas(self, rango):
        hoy = datetime.now().date()

        # Mapeo de opciones predefinidas
        rangos = {
            "Últimos 30 días": relativedelta(days=30),
            "Últimos 60 días": relativedelta(days=60),
            "Últimos 90 días": relativedelta(days=90),
            "Este mes": relativedelta(day=1),
            "Últimos 6 meses": relativedelta(months=6),
            "Este año": relativedelta(month=1, day=1)
        }

        if rango == "Personalizado":
            # Widget para selección manual de fechas
            cols = st.columns(2)
            with cols[0]:
                fecha_inicio = st.date_input("Fecha inicio", value=hoy - timedelta(days=30))
            with cols[1]:
                fecha_fin = st.date_input("Fecha fin", value=hoy)
            return fecha_inicio, fecha_fin
        
        elif rango in rangos:
            delta = rangos[rango]
            
            # Caso especial para mes anterior
            if rango == "Mes anterior":
                fecha_inicio = (hoy + delta[0]).replace(day=1)
                fecha_fin = hoy + delta[1]
            else:
                fecha_inicio = hoy - delta
                fecha_fin = hoy
            
            return fecha_inicio, fecha_fin
        
        else:
            st.error("Rango no válido")
            return hoy, hoy