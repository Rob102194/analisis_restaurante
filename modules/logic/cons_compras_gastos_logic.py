
class ConsultasComprasGastosLogic:
    def __init__(self, data_service):
        self.data_service = data_service
        self.last_query = None

    def consultar_registros(self, filtros: dict) -> list:
        return self.data_service.obtener_registros(
            tipo=filtros["categoria"],
            filtros=filtros
        )
    
