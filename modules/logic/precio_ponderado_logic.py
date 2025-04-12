import pandas as pd

class PrecioPonderadoLogic:
    def __init__(self, data_service):
        self.data_service = data_service
    
    def obtener_productos(self):
        """Usar el método de DataService"""
        return self.data_service.obtener_productos()

    def obtener_precios_historicos(self, producto, fecha_inicio, fecha_fin):
        filtros  = {
            "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),  
            "fecha_fin": fecha_fin.strftime("%Y-%m-%d"),        
            "producto": producto
        }

        data = self.data_service.obtener_registros(tipo="mercancía", filtros=filtros)
        df = pd.DataFrame(data)

        if not df.empty:
            df['precio_unitario'] = df['monto'] / df['cantidad']
            df['fecha'] = pd.to_datetime(df['fecha'])
            df = df.sort_values('fecha')
        return df
    
    def calcular_precio_ponderado(self, df):
        if df.empty:
            return 0
        return df['monto'].sum() / df['cantidad'].sum()