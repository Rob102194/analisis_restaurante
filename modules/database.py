import streamlit as st
from supabase import create_client
import pandas as pd
from utils.error_handler import ErrorHandler

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._inicializar_conexion()
        return cls._instance
    
    def _inicializar_conexion(self):
        """Establece la conexión única con Supabase"""
        self.client = create_client(
            st.secrets["SUPABASE_URL"].strip(),
            st.secrets["SUPABASE_KEY"].strip()
        )
        self._create_tables()

    def _create_tables(self):
        """Crear todas las tablas necesarias"""
        
        tables =  {
            "compras": """
                CREATE TABLE IF NOT EXISTS compras (
                    id SERIAL PRIMARY KEY,
                    fecha DATE NOT NULL,
                    categoria VARCHAR(50) NOT NULL DEFAULT 'Mercancía',
                    producto VARCHAR(100),
                    cantidad NUMERIC(10,3) NOT NULL DEFAULT 1,
                    unidad_medida VARCHAR(20) NOT NULL DEFAULT 'unidad',
                    monto NUMERIC(10,2) NOT NULL,
                    proveedor VARCHAR(100),
                    descripcion TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """,

            "gastos": """
                CREATE TABLE IF NOT EXISTS gastos (
                    id SERIAL PRIMARY KEY,
                    fecha DATE NOT NULL,
                    producto VARCHAR(100),
                    categoria VARCHAR(50) NOT NULL,
                    monto NUMERIC(10,2) NOT NULL,
                    descripcion TEXT,
                    proveedor VARCHAR(100),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """,

            "ventas": """
                CREATE TABLE IF NOT EXISTS ventas (
                    id SERIAL PRIMARY KEY,
                    fecha DATE NOT NULL,
                    grupo VARCHAR(50) NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    cantidad INTEGER NOT NULL,
                    venta NUMERIC(10,2) NOT NULL,
                    entidad VARCHAR(20) NOT NULL CHECK (entidad IN ('restaurante', 'domicilio')),
                    cliente VARCHAR(20) NOT NULL CHECK (cliente IN ('clientes', 'cuenta_casa')),
                    created_at TIMESTAMP DEFAULT NOW()
            )
        """
        }

        for tables, script in tables.items():
            self.client.rpc('execute_sql', params={'query': script}).execute()
    
    def safe_insert(self, target_table: str, data: dict) -> dict:
        try:
            # Limpiar valores NaN/None
            data_limpia = {k: v if not pd.isna(v) else None for k, v in data.items()}
    
            # Insertar
            response = self.client.table(target_table).insert(data_limpia).execute()
            
            if not response.data:
                raise ValueError("No se recibieron datos de respuesta")
                
            return response.data[0]
            
        except Exception as e:
            error_msg = f"""
            Error en tabla {target_table}:
            - Datos: {data_limpia}
            - Error: {str(e)}
            """
            st.error(error_msg)
            raise

    def actualizar_registro(self, tabla: str, registro_id: int, nuevos_datos: dict) -> bool:
        try:
            self.client.table(tabla).update(nuevos_datos).eq('id', registro_id).execute()
            return True
        except Exception as e:
            st.error(f"Error actualizando registro: {str(e)}")
            return False
    
    def eliminar_registro(self, tabla: str, registro_id: int) -> bool:
        try:
            # Verificar existencia del registro
            registro = self.client.table(tabla).select("*").eq('id', registro_id).execute()
            if not registro.data:
                st.error(f"Registro {registro_id} no existe en {tabla}")
                return False
                
            # Ejecutar eliminación
            self.client.table(tabla).delete().eq('id', registro_id).execute()
            st.toast(f"🗑️ Registro {registro_id} eliminado")
            return True
            
        except Exception as e:
            error_msg = f"""
            **Error eliminando registro**  
            Tabla: {tabla}  
            ID: {registro_id}  
            Detalles: {str(e)}
            """
            st.error(error_msg)
            return False
    
    def execute_safe_operation(self, operation, table, data=None, record_id=None):
            try:
                if operation == 'insert':
                    return self.safe_insert(table, data)
                elif operation == 'update':
                    return self.actualizar_registro(table, record_id, data)
                elif operation == 'delete':
                    return self.eliminar_registro(table, record_id)
            except Exception as e:
                ErrorHandler.handle_db_error(e, f"{operation} en {table}")
                raise



















    