import cv2
import pytesseract 
import numpy
import time
from PIL import ImageGrab
import json
import pprint


def zoom(img, zoom_factor=2):
    return cv2.resize(img, None, fx=zoom_factor, fy=zoom_factor)

pytesseract.pytesseract.tesseract_cmd = r'/Users/genkisystem/opt/anaconda3/envs/isso/bin/tesseract'

path_to_save = "img_out/"
path = "class_ocr/temp/2021-11-24T10_08_06.375314/1-04123cc0-abc5-4791-8ac6-b5303f4365b2.png"
# path = "/Users/genkisystem/Desktop/ISSO_2/class_ocr/test/image_13.png"
img = cv2.imread(path)
h_, w_ = img.shape[:-1] 

cropped_image = img.copy()[100:350, 0: int(w_/3*2)]
gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
_, thrash = cv2.threshold(gray_image, 230, 255, cv2.THRESH_BINARY)  

thrasss = cv2.bitwise_not(thrash)
cv2.imshow('thrasss',thrasss)
cv2.waitKey(0)
zoom_img = zoom(thrasss, zoom_factor=1.2) 

text = pytesseract.image_to_string(zoom_img, 'jpn+eng') 
data = pytesseract.image_to_data(zoom_img, lang='jpn+eng',output_type='dict',)
boxes = len(data['level'])
print(data['text'])
print(data['level'])
print(data.keys())
for i in range(boxes ):
    # if data['text'][i] in ['広告','お', 'すす', 'め','ショ', 'ッ', 'プ', 'を', '見', 'る']:
    print('=====', data['text'][i], {
        'level': data['level'][i],
        'page_num': data['page_num'][i],
        # 'block_num': data['block_num'][i],
        # 'par_num': data['par_num'][i],
        # 'line_num': data['line_num'][i],
        # 'word_num': data['word_num'][i],
        'left': data['left'][i],
        'top': data['top'][i],
        'width': data['width'][i],
        'height': data['height'][i]
    })
            
        
        
        
        
        
    print('======\t')
    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
    #Draw box        
    cv2.rectangle(zoom_img, (x, y), (x + w, y + h), (0, 0,0), 2)

cv2.imshow('img',zoom_img)
cv2.waitKey(0)
# hImg, wImg,_ = img.shape
# boxes = pytesseract.image_to_boxes(img)
# ROI_number=0
# for b in boxes.splitlines():
#     b = b.split(' ')
#     x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
#     # cv2.rectangle(img, (x,hImg- y), (w,hImg- h), (50, 50, 255), 1)
#     x1,y1=hImg-h,hImg-y
#     x2,y2=x,w
#     roi=img[x1:y1,x2:y2]
#     output = cv2.resize(roi,(300,300))
#     cv2.imshow('roi', roi)
#     cv2.waitKey(0)
#     cv2.imshow('img',img)
#     cv2.waitKey(0)
#     # cv2.imwrite("test"+str(ROI_number)+".jpeg",output)
#     ROI_number+=1