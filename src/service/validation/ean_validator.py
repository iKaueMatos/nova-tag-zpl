# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
class EANValidator:
    @staticmethod
    def is_valid_ean(ean):
        """Verifica se o EAN possui 8, 12, 13 ou 14 dígitos."""
        return len(ean) in [8, 12, 13, 14] and ean.isdigit()
