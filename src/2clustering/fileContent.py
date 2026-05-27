from pathlib import Path
import fitz
import pytesseract
from PIL import Image

class FileContent:
    def __init__(self):
        self.txt = {'.txt', '.md', '.csv', '.json', '.py', '.js', '.html'}
        self.pdf = {'.pdf'}
        self.img = {'.png', '.jpg', '.jpeg'}

    def _txtExtract(self, filePath: Path):
        with open(filePath, 'r', encoding='utf-8') as txt:
            content = txt.read()
        return content if content else ""

    def _pdfExtract(self, filePath: Path):
        text = ""
        with fitz.open(filePath) as doc:
            for page in doc:
                text += page.get_text('text')
        return text

    def _imgExtract(self, filePath: Path):
        text = pytesseract.image_to_string(Image.open(filePath))
        return text if text else ""

    def extract(self, filePath: Path):
        ext = filePath.suffix.lower()
        if ext in self.txt:
            return self._txtExtract(filePath)
        elif ext in self.pdf:
            return self._pdfExtract(filePath)
        elif ext in self.img:
            return self._imgExtract(filePath)
        else:
            return ""