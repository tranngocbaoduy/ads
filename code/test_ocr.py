import pytesseract
import os
from glob import glob
from PIL import Image, ImageEnhance, ImageFilter

pytesseract.pytesseract.tesseract_cmd = r'/Users/genkisystem/opt/anaconda3/envs/isso/bin/tesseract'

def get_text_from_image(image_path, lang='jpn'):
    text = pytesseract.image_to_string(Image.open(path), lang)
    return text

def is_collect(text):
    if '広告' in text or 'おすすめ' in text: return True
    return False

def category_text(text):
    if 'おすすめ' in text: return "suggest"
    if '広告' in text: return "ads"
    return "ads"

def handle_collect(image_path):
    text = get_text_from_image(image_path)
    is_collect_image = is_collect(text)
    if is_collect_image:
        direction = category_text(text)
        print(image_path, direction)

# parent_path = "/Users/genkisystem/Desktop/class_ocr/suggest_for_you/"
parent_path = "/Users/genkisystem/Desktop/class_ocr/fb/sponsor"

child_path_imgs = glob(os.path.join(parent_path,'*.png'))
print('chil',child_path_imgs)

suggestion_path = []
ads_path = []
wrong_path = []
for path in child_path_imgs:
    handle_collect(path) 
