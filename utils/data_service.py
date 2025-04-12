from modules.database import DatabaseManager 

class DataService:
    def __init__(self,db_manager: DatabaseManager):
        self.db = db_manager
        
    def obtener_registros(self, tipo: str, filtros: dict) -> list:
        tabla = "compras" if tipo == "mercancía" else "gastos"
        query = self.db.client.table(tabla).select("*")
        
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