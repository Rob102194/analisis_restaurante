from streamlit import column_config
from datetime import datetime

class ColumnConfigFactory:
    @staticmethod
    def get_column_configs():
        return {
            "fecha": column_config.DateColumn(
                "Fecha", format="YYYY-MM-DD", 
                default=datetime.today().date()
            ),
            "categoria": column_config.SelectboxColumn(
                "Categoría", 
                options=["mercancía", "equipos", "nomina", "servicios", "otros"]
            ),
            "monto": column_config.NumberColumn(
                "Monto ($)", 
                format="%.2f", 
                required=True, 
                min_value=0.01
            ),
            "unidad_medida": column_config.SelectboxColumn(
                "Unidad", 
                options=["unidad", "kg", "litros", "paquete"], 
                required=True
                
            ),
            "cantidad": column_config.NumberColumn(
                "Cantidad", 
                format="%.3f", 
                required=True
            )
        }
    
