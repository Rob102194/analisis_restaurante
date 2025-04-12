from modules.database import DatabaseManager 

class DataService:
    def __init__(self,db_manager: DatabaseManager):
        self.db = db_manager
        
    def obtener_registros(self, tipo: str, filtros: dict) -> list:
        """Obtiene registros filtrados por tipo (compras/gastos)"""
        tabla = "compras" if tipo.lower() == "mercancía" else "gastos" 
        query = self.db.client.table(tabla).select("*")
        
        # Aplicar filtros
        if filtros.get("fecha_inicio"):
            query = query.gte("fecha", filtros["fecha_inicio"])
        if filtros.get("fecha_fin"):
            query = query.lte("fecha", filtros["fecha_fin"])
        if filtros.get("producto"):
            query = query.ilike("producto", f"%{filtros['producto']}%")
    
        return query.execute().data

    def guardar_registro(self, tipo: str, datos: dict):
        return self.db.execute_safe_operation(
            operation='insert',
            table="compras" if tipo == "mercancía" else "gastos",
            data=datos
        )
    
    def obtener_productos(self):
        """Obtiene lista única de productos registrados"""
        try:
            # Consultar productos distintos
            response = self.db.client.table("compras").select("producto").execute()
            productos = list({item["producto"] for item in response.data if item["producto"]})
            return sorted(productos)
        except Exception as e:
            print(f"Error obteniendo productos: {str(e)}")
            return []
        
        