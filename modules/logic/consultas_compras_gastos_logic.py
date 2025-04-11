
class ConsultasComprasGastosLogic:
    def __init__(self, db_manager):
        self.db = db_manager
        self.last_query = None

    def consultar_registros(self, filtros: dict) -> list:
        tabla = "compras" if filtros["categoria"] == "mercancía" else "gastos"
        
        query = self.db.client.table(tabla).select("*")
        
        if filtros["fecha_inicio"]:
            query = query.gte("fecha", filtros["fecha_inicio"])
        if filtros["fecha_fin"]:
            query = query.lte("fecha", filtros["fecha_fin"])
        if filtros["producto"]:
            query = query.ilike("producto", f"%{filtros['producto']}%")
        
        self.last_query = query
        return query.execute().data
    
