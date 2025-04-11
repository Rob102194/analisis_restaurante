import pandas as pd
from datetime import datetime

def procesar_dataframe_editado(edited_df: pd.DataFrame) -> list[dict]:
    edited_data = edited_df.replace({pd.NA: None}).to_dict('records')
    
    for registro in edited_data:
        try:
            # Validación básica para mercancía
            if registro.get('categoria') == 'mercancía':
                if registro.get('cantidad') is None:
                    raise ValueError("Cantidad es obligatoria para mercancía")
                if registro.get('unidad_medida') is None:
                    raise ValueError("Unidad de medida es obligatoria para mercancía")
            
            # Resto del procesamiento
            if 'fecha' in registro:
                registro['fecha'] = pd.to_datetime(registro['fecha']).strftime("%Y-%m-%d")
            
            monto = registro.get('monto')
            if monto is None or (isinstance(monto, str) and monto.strip() == ''):
                raise ValueError("El campo 'monto' no puede estar vacío")
            registro['monto'] = float(monto)  # Conversión después de validar

            # Para cantidad (solo mercancía)
            if registro.get('categoria') == 'mercancía':
                cantidad = registro.get('cantidad')
                if cantidad is None or (isinstance(cantidad, str) and cantidad.strip() == ''):
                    raise ValueError("Cantidad es obligatoria para mercancía")
                registro['cantidad'] = float(cantidad)
        
        except ValueError as e:
            identificador = (
                f"Producto: '{registro.get('producto', 'N/A')}' | "
                f"Fecha: {registro.get('fecha', 'N/A')} | "
                f"Categoría: {registro.get('categoria', 'N/A')}"
            )
            raise ValueError(f"Error en registro [{identificador}]: {str(e)}")
    
    return edited_data

 