class ValidadorRegistros:
    @staticmethod
    def validar_campos_comunes(registro):
        errores = []
        
        # Campos base (obligatorios para todas las tablas)
        if not registro.get('fecha'):
            errores.append("**Fecha** no especificada")
        if not registro.get('categoria'):
            errores.append("**Categoría** es obligatoria")
        if not registro.get('producto', "").strip():
            errores.append("**Producto** no especificado")
        
        monto = registro.get('monto')
        if monto is None or (isinstance(monto, str) and monto.strip()) == '':
            errores.append("**Monto** no especificado")  
        else:
            try:
                monto_float = float(monto)
                if monto_float <= 0:
                    errores.append("**Monto** debe ser mayor a $0")
            except (TypeError, ValueError):
                errores.append("Formato de **monto** inválido")

        # Validación de CANTIDAD (solo para mercancía)
        if registro.get("categoria") == "mercancía":
            cantidad = registro.get('cantidad')
            if cantidad is None or (isinstance(cantidad, str) and cantidad.strip() == ''):
                errores.append("**Cantidad** no especificada") 
            else:
                try:
                    cantidad_float = float(cantidad)
                    if cantidad_float <= 0:
                        errores.append("**Cantidad** debe ser > 0")
                except (TypeError, ValueError):
                    errores.append("Formato de **cantidad** inválido")
            if not registro.get('unidad_medida'):
                errores.append("**Unidad de medida** requerida")
        
        return errores

    @staticmethod
    def filtrar_campos(registro):
        campos_permitidos = ['fecha', 'categoria', 'producto', 'monto']
        
        if registro.get("categoria") == "mercancía":
            campos_permitidos += ['cantidad', 'unidad_medida']
        
        # Eliminar campos no permitidos y limpiar None
        reg_filtrado = {}
        for campo in campos_permitidos:
            valor = registro.get(campo)
            if valor is not None:  # <-- Clave!
                reg_filtrado[campo] = valor
        
        return reg_filtrado

    @staticmethod
    def obtener_tabla(registro):
        return "compras" if registro.get("categoria") == "mercancía" else "gastos"
    
    @staticmethod
    def construir_mensaje_error(errores, contexto="registro"):
        mensaje = f"**🚨 Errores en {contexto.capitalize()}**\n\n"
        mensaje += "\n".join([f"• {e}" for e in errores])
        mensaje += "\n\n**🔧 Acción requerida:**\nCorrige los campos señalados."
        return mensaje