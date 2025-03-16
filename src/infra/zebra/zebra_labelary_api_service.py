import re
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import io

from src.core.config.enum.label_format_constants import LabelFormatConstants

class ZebraLabelaryApiService:
    def generate_preview_image(self, zpl_code, printer_density="8dpmm", label_dimensions="5x2.5", label_index="0", output_format="image/png"):
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

    def generate_pdf(self, zpl_code, printer_density="8dpmm", label_dimensions="5x2.5", label_index="0"):
        """
            Envia o ZPL para a API do Labelary e retorna um objeto PDF
            caso tenha sucesso, ou None em caso de erro.
        """
        try:
            if not label_dimensions:
                label_dimensions = self.extract_label_dimensions(zpl_code)

            if not label_dimensions:
                print("Não foi possível determinar as dimensões da etiqueta.")

            url = f"{LabelFormatConstants.BASE_URL}/{printer_density}/labels/{label_dimensions}/{label_index}"

            files = {'file': zpl_code}
            headers = {'Accept': 'application/pdf'}

            response = requests.post(url, files=files, headers=headers)

            if response.status_code == 200:
                pdf_data = response.content
                return pdf_data
            else:
                print(f"Labelary API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return None

    def extract_label_dimensions(self, zpl_code):
        height_match = re.search(r"^LL(\d+)", zpl_code, re.MULTILINE)
        width_match = re.search(r"^PW(\d+)", zpl_code, re.MULTILINE)

        if height_match and width_match:
            height_in_inches = int(height_match.group(1)) / 203.0
            width_in_inches = int(width_match.group(1)) / 203.0

            return f"{width_in_inches:.2f}x{height_in_inches:.2f}"
        return None

    def update_preview(self, zpl_code, label_format, preview_image_label):
        """
            Gera a imagem a partir do ZPL (via Labelary) e exibe no Label de preview.
        """
        if not zpl_code:
            return

        if label_format is None:
            messagebox.showerror("Erro", "Selecione um formato de etiqueta.")
            return

        def get_first_zpl_block(zpl_code):
            if "^XZ" in zpl_code:
                first_block = zpl_code.split("^XZ")[0] + "^XZ"
                return first_block
            return None

        zpl_code_to_send = get_first_zpl_block(zpl_code)

        if not zpl_code_to_send:
            messagebox.showerror("Erro", "Código ZPL inválido ou não encontrado.")
            return

        if label_format == "2-Colunas":
            printer_density = LabelFormatConstants.PRINTER_DENSITY_8DPMM
            label_dimensions = LabelFormatConstants.LABEL_DIMENSIONS_5X25
            label_index = LabelFormatConstants.LABEL_INDEX_0
            output_format = LabelFormatConstants.OUTPUT_FORMAT_IMAGE

        if label_format == "1-Coluna":
            printer_density = LabelFormatConstants.PRINTER_DENSITY_8DPMM
            label_dimensions = LabelFormatConstants.LABEL_DIMENSIONS_5X25
            label_index = LabelFormatConstants.LABEL_INDEX_0
            output_format = LabelFormatConstants.OUTPUT_FORMAT_IMAGE

        image = self.generate_preview_image(
            zpl_code_to_send,
            printer_density,
            label_dimensions,
            label_index,
            output_format
        )

        if image:
            width, height = image.size
            new_width = 600
            new_height = int((new_width / width) * height)
            image = image.resize((new_width, new_height), Image.LANCZOS)

            preview_image_tk = ImageTk.PhotoImage(image)
            preview_image_label.config(image=preview_image_tk)
            preview_image_label.image = preview_image_tk
        else:
            messagebox.showerror("Erro", "Falha ao gerar a pré-visualização da etiqueta.")