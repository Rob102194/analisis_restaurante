import pandas as pd
from utils.error_handler import ErrorHandler

def validate_mercancia_fields(registro):
    if registro.get('categoria') == 'mercancía':
        errors = []
        if not registro.get('cantidad'):
            errors.append("Cantidad es obligatoria para mercancía")
        if not registro.get('unidad_medida'):
            errors.append("Unidad de medida es obligatoria para mercancía")
        return errors
    return []

def procesar_dataframe_editado(edited_df: pd.DataFrame) -> list[dict]:
    edited_data = edited_df.replace({pd.NA: None}).to_dict('records')
    
    for registro in edited_data:
        try:
            if 'fecha' in registro:
                registro['fecha'] = pd.to_datetime(registro['fecha']).strftime("%Y-%m-%d")
            
            monto = registro.get('monto')
            if monto is None or (isinstance(monto, str) and monto.strip() == ''):
                raise ValueError("El campo 'monto' no puede estar vacío")
            registro['monto'] = float(monto)  # Conversión después de validar

            # Para mercancías
            mercancia_errors = validate_mercancia_fields(registro)
            if mercancia_errors:
                raise ValueError("\n".join(mercancia_errors))
        
        except ValueError as e:
            identificador = (
                f"Producto: '{registro.get('producto', 'N/A')}' | "
                f"Fecha: {registro.get('fecha', 'N/A')} | "
                f"Categoría: {registro.get('categoria', 'N/A')}"
            )
            ErrorHandler.display_validation_errors(
                errors=[str(e)], 
                context=f"procesamiento de datos - {identificador}"
            )
    
    return edited_data

 