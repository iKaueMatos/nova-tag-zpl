# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
import yaml

class RoutesScreen:
    def __init__(self):
        self.routes = self.load_routes()

    def load_routes(self):
        with open('routes.yaml', 'r') as file:
            return yaml.safe_load(file)

    def get_routes(self):
        return self.routes