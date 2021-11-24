import cv2
import pytesseract 
import numpy
import time
from PIL import ImageGrab
import json
import pprint

pytesseract.pytesseract.tesseract_cmd = r'/Users/genkisystem/opt/anaconda3/envs/isso/bin/tesseract'

path_to_save = "img_out/"
path = "class_ocr/temp/1111-98b88ef6-9220-4b52-bf69-d9b17d28d620.png"
# path = "/Users/genkisystem/Desktop/ISSO_2/class_ocr/test/image_13.png"
img = cv2.imread(path)
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  
img_blur = cv2.GaussianBlur(img_gray, (3,3), 0)

edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200) # Canny Edge Detection
# Display Canny Edge Detection Image
cv2.imshow('Canny Edge Detection', edges)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('./assets/small.png', edges)
 
import cv2
import numpy as np
 
# mask = cv2.threshold(img[:, :, 0], 255, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

stats = cv2.connectedComponentsWithStats(edges, 8)[2]
label_area = stats[1:, cv2.CC_STAT_AREA]
print('label_area',label_area)
min_area, max_area = 148, 160  # min/max for a single circle
singular_mask = (min_area < label_area) & (label_area <= max_area)
circle_area = np.mean(label_area[singular_mask])

n_circles = int(np.sum(np.round(label_area / circle_area)))

print('Total circles:', n_circles)

# data = pytesseract.image_to_data(img, lang='jpn',output_type='dict',)
# boxes = len(data['level'])
# print(data['text'])
# print(data['level'])
# print(data.keys())
# for i in range(boxes ):
#     if data['text'][i] in ['お', 'すす', 'め']:
#         print('=====', data['text'][i], {
#             'level': data['level'][i],
#             'page_num': data['page_num'][i],
#             # 'block_num': data['block_num'][i],
#             # 'par_num': data['par_num'][i],
#             # 'line_num': data['line_num'][i],
#             # 'word_num': data['word_num'][i],
#             'left': data['left'][i],
#             'top': data['top'][i],
#             'width': data['width'][i],
#             'height': data['height'][i]
#         })
        
        
        
        
        
        
#         print('======\t')
#     (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
#     #Draw box        
#     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
 