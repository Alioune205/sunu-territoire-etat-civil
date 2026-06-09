from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

print("Version :", pytesseract.get_tesseract_version())

img = Image.open("test.jpg")

text = pytesseract.image_to_string(
    img,
    lang="fra"
)

print(text)