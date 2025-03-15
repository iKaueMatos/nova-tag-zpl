import re

import requests
from PIL import Image
import io

from src.core.config.enum.label_format_constants import LabelFormatConstants

class ZebraLabelaryApiService:
    def generate_preview_image(self, zpl_code, printer_density="8dpmm", label_dimensions="5x2.5", label_index="0", output_format="image/png", calculate=False):
        """
            Envia o ZPL para a API do Labelary e retorna um objeto PIL.Image
            caso tenha sucesso, ou None em caso de erro.
        """
        try:
            if not label_dimensions:
                label_dimensions = self.extract_label_dimensions(zpl_code)

            if not label_dimensions:
                print("Não foi possível determinar as dimensões da etiqueta.")

            url = f"{LabelFormatConstants.BASE_URL}/{printer_density}/labels/{label_dimensions}/{label_index}"

            files = {'file': zpl_code}
            headers = {'Accept': output_format}

            response = requests.post(url, files=files, headers=headers)

            if response.status_code == 200:
                image_data = response.content
                image = Image.open(io.BytesIO(image_data))
                return image
            else:
                print(f"Labelary API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Erro ao gerar preview: {e}")
            return None

    def extract_label_dimensions(zpl_code):
        height_match = re.search(r"^LL(\d+)", zpl_code, re.MULTILINE)
        width_match = re.search(r"^PW(\d+)", zpl_code, re.MULTILINE)

        if height_match and width_match:
            height_in_inches = int(height_match.group(1)) / 203.0
            width_in_inches = int(width_match.group(1)) / 203.0

            return f"{width_in_inches:.2f}x{height_in_inches:.2f}"
        return None