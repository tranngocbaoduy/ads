import re
import argparse
import os
import sys
import shutil
import subprocess
import json 
import pytesseract 
import cv2 
import pprint
import numpy as np 
import datetime

from glob import glob
from skimage.metrics import structural_similarity as ssim
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'/Users/genkisystem/opt/anaconda3/envs/isso/bin/tesseract'

file_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.abspath(file_dir + '/..')
run_time_iso_date = datetime.datetime.utcnow().isoformat().replace(':','_') 

MAIN_PATH = "/Users/genkisystem/Desktop/ISSO_2/class_ocr"
APP_PATH = "twitter"
CATEGORY_ADS_PATH = "promoted"

def log(message, _type = 'INFO'):
    print('{} [{}]: {}'.format(datetime.datetime.utcnow().isoformat(),_type,message))

def copy_file(src, dst):
    head, tail = os.path.split(src)
    src_dir = head
    file_name = tail

    head, tail = os.path.split(dst)
    dst_dir = head
 
    if not os.path.isdir(src_dir): os.makedirs(src_dir)
    if not os.path.isdir(dst_dir): os.makedirs(dst_dir) 
    shutil.move(src, dst)
 
def get_text_from_image(image_path, lang='jpn'):
    text = pytesseract.image_to_string(Image.open(image_path), lang)
    return text

def is_collect(paragraph): 
    allow_texts = ['ショップを見る', 'Sponsored', '広告', 'おすすめ', 'Promoted']
    for allow_text in allow_texts:
        if allow_text in paragraph: return True
    return False

def category_text(text):
    if 'おすすめ' in text: return "suggest"
    if 'Promoted' in text or 'Sponsored' in text: return "ads"
    if 'ショップを見る' in text: return "product"
    return "ads"

def handle_collect(image_path):
    lang = 'eng+lng'
    text = get_text_from_image(image_path,lang=lang) 
    is_collect_image = is_collect(text.strip())
    if is_collect_image:
        type_ads = category_text(text)

        # scroll to element
        top_position = get_closest_position(image_path)
        scroll_up(driver, top_position)

        # take picture again
        image_path = get_screen_shoot(driver,path=image_path)

        if type_ads == 'ads': dst_path = os.path.join(MAIN_PATH, 'category',APP_PATH, run_time_iso_date,CATEGORY_ADS_PATH)
        if type_ads == 'suggest': dst_path = os.path.join(MAIN_PATH, 'category',APP_PATH, run_time_iso_date, CATEGORY_SUGGEST_PATH)
        if type_ads == 'product': dst_path = os.path.join(MAIN_PATH, 'category',APP_PATH, run_time_iso_date, CATEGORY_PRODUCT_PATH)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        head, tail = os.path.split(image_path)
        dst_path = os.path.join(dst_path, tail)
        copy_file(image_path, dst_path) 
        return True, type_ads, dst_path 
    return False, None, ""


def check_is_product_ads_by_img(image_path): 
    list_image_path = glob("./assets/icon/ins_simple/*shop*.png")
    output_image = cv2.imread(image_path) 
    input_image = output_image.copy()
    threshold = .28 
    h_, w_ = output_image.shape[:-1] 
    threshold_pos_y = h_ / 2
    threshold_pos_x = (w_ / 2 - 63, w_ / 2 + 63)
    position_image = tuple() 
    # Read the images from the file
    for icon_path in list_image_path:
        small_image = cv2.imread(icon_path)
        small_image_gray = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)
        h, w = small_image.shape[:-1]
        result = cv2.matchTemplate(small_image, output_image, cv2.TM_CCOEFF_NORMED)
        
        loc = np.where(result >= threshold)
        for position in zip(*loc[::-1]):  # Switch collumns and rows
            # handle with product ads
            if position[0] < threshold_pos_x[0]:
                cropped_image = input_image.copy()[position[1]:position[1]+h,position[0]:position[0]+w].copy()
                cropped_image_gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
                score, diff = compare_image(cropped_image_gray, small_image_gray)
                
                if score < 0.5: continue 
                position_image = (position[0], position[0] + w, position[1], position[1] + h) 
                cv2.rectangle(output_image, position, (position[0] + w, position[1] + h), (0, 255, 0), 2)
                return True, position_image
    return False, position_image


def get_activity(driver): 
    activity = driver.current_activity
    print('activity',activity)
    return activity
  
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction

def record_video(driver, path):
    driver.start_recording_screen() 
    print('start record')
    time.sleep(15)
    video = driver.stop_recording_screen(
        #remotePath="/Users/genkisystem/Desktop/test.mp4"
    ) 
    print('stop record')
    fh = open("{}".format(path), "wb")
    fh.write(base64.b64decode(video))
    print('save record')
    time.sleep(10) 
    fh.close()


# from selenium import webdriver
def scroll_down(driver): 
    size = driver.get_window_size()
    padding = 500
    max_height = size['height'] - padding
    max_width = size['width'] - padding
    
    middle_width = round(max_width / 2)
    middle_height = round(max_height / 2) 

    driver.swipe(middle_width, middle_height , middle_width, -middle_height, 2000)  

def scroll_up(driver, top): 
    size = driver.get_window_size()
    padding = 500
    max_height = size['height'] - padding
    max_width = size['width'] - padding
    
    middle_width = round(max_width / 2)
    middle_height = round(max_height / 2)
    header_height = top + 400 if top > middle_height else 1700
    print("Scroll up", 'from {} to {}'.format(middle_height, middle_height - top + header_height))
    driver.swipe(max(middle_width - 400,200), middle_height , middle_width, middle_height - top + header_height, 3000)  
     
def scroll_to_right(driver): 
    time.sleep(0.2)
    size = driver.get_window_size()
    padding = 500
    max_height = size['height'] - padding
    max_width = size['width'] - padding
    
    middle_width = round(max_width / 2) + 50
    middle_height = round(max_height / 2) + 220

    print('middle_height',max_height,middle_height)
    print('middle_width',max_width,middle_width)
    driver.swipe(1800, middle_height , 0, middle_height+50, 2000)  
    time.sleep(0.5)
 

def get_screen_shoot(driver, i='default', path = ""): 
    image = base64.b64decode(driver.get_screenshot_as_base64())   
    image_dir =  os.path.join(MAIN_PATH, "temp", run_time_iso_date)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    image_path = os.path.join(image_dir, str(i)+"-"+ str(uuid.uuid4())+".png")
    img = Image.open(io.BytesIO(image))
    if len(path) == 0:
        img.save(image_path, 'png')
        return image_path
    else:
        img.save(path, 'png')
        return path

def get_list_ele_by_xpath(driver, xpath):
    return driver.find_elements_by_xpath(xpath)

def get_list_ele_by_id(driver): 
    return driver.find_element_by_id('android:id/list')
    #instagram
    # return driver.find_element_by_id('com.instagram.android:id/row_feed_profile_header')

def get_list_post_element(driver, app_name):
    if app_name == 'facebook':
        xpath = '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/androidx.recyclerview.widget.RecyclerView/android.view.ViewGroup'
    if app_name == 'twitter':
        xpath = '//androidx.recyclerview.widget.RecyclerView[@content-desc="Home timeline list"]/android.view.ViewGroup'
    # if app_name == 'line':
    # if app_name == 'instagram':
    return get_list_ele_by_xpath(driver, xpath)

def get_closest_position(path):
    
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    data = pytesseract.image_to_data(img, lang='jpn',output_type='dict',)
    boxes = len(data['level']) 
    collect_words = []
    ## filter collectable word
    allow_text = ['Promoted','広告','お', 'すす', 'め','ショップを見る', 'Sponsored', '広告', 'おすすめ','ショ', 'ッ', 'プ', 'を', '見', 'る']

    for i in range(boxes ):
        if data['text'][i] in allow_text:
            obj = {
                'text': data['text'][i],
                'level': data['level'][i],
                'page_num': data['page_num'][i],
                'block_num': data['block_num'][i],
                'par_num': data['par_num'][i],
                'line_num': data['line_num'][i],
                'word_num': data['word_num'][i],
                'left': data['left'][i],
                'top': data['top'][i],
                'width': data['width'][i],
                'height': data['height'][i]
            }
            collect_words.append(obj)
     
    ## filter word by line num
    line_nums_filter = {}
    for obj in collect_words:
        if obj['text'] in ['ショップを見る', 'Promoted','Sponsored', '広告', 'おすすめ']:
            return obj['top'] 
        if not str(obj['line_num']) in line_nums_filter.keys():
            line_nums_filter[str(obj['line_num'])] = [obj]
        else:
            line_nums_filter[str(obj['line_num'])].append(obj)

    for key, objs in line_nums_filter.items():
        if len(objs) == 3:
            return objs[0]['top']
    return 0

def compare_image(img1, img2):
    (score, diff) = ssim(img1, img2, full=True)
    return score, diff

def check_is_different(img1_path, img2_path):  
    image_1 = cv2.imread(img1_path)
    image_1 = cv2.cvtColor(image_1, cv2.COLOR_BGR2GRAY)  

    image_2 = cv2.imread(img2_path)
    image_2 = cv2.cvtColor(image_2, cv2.COLOR_BGR2GRAY) 

    score, diff = compare_image(image_1, image_2)
    if score > 0.98:
        return False
    return True

def check_is_carousel(driver):
    # get_screen_shoot_1 
 
    image_path_1 = get_screen_shoot(driver,path="./class_ocr/temp/temp1.png") 
    image_1 = cv2.imread(image_path_1)
    image_1 = cv2.cvtColor(image_1, cv2.COLOR_BGR2GRAY) 

    scroll_to_right(driver)
 
    # get_screen_shoot_2
    image_path_2 = get_screen_shoot(driver,path="./class_ocr/temp/temp2.png")
    image_2 = cv2.imread(image_path_2)
    image_2 = cv2.cvtColor(image_2, cv2.COLOR_BGR2GRAY) 

    score, diff = compare_image(image_1, image_2)
    if score > 0.98:
        return False
    return True

def footage_to_frame(video):
    vidcap = cv2.VideoCapture(video)
    frames = []

    #  read until no more frames exist in the video
    while True:
        success, frame = vidcap.read()
        if (success):
            frames.append(frame)
        else:
            #  unable to read a frame
            break
 
    return frames

def frames_to_base64(frames):
    frames_b64 = []
    #  iterate frames and convert each of them to base64
    for frame in frames:
        frames_b64.append(base64.b64encode(frame))
    return frames_b64

def find_triangle_twitter(input_image):  
    #convert image into greyscale mode
    list_triangle = []
    gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

    #find threshold of the image
    _, thrash = cv2.threshold(gray_image, 230, 255, cv2.THRESH_BINARY) 
    contours, _ = cv2.findContours(thrash, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
    for contour in contours:
        # check area of contour must be in range 750 ~ 800
        if cv2.contourArea(contour) < 750 or cv2.contourArea(contour) > 800: continue
        shape = cv2.approxPolyDP(contour, 0.1*cv2.arcLength(contour, True), True)
        x_cor = shape.ravel()[0]
        y_cor = shape.ravel()[1]

        #For triangle
        if len(shape) ==3:
            list_triangle.append(shape)
    return list_triangle

def check_is_has_play_btn(path):
    input_image = cv2.imread(path)
    output = input_image.copy()
    h_, w_ = input_image.shape[:-1]
    threshold_pos_x = (w_ / 2 - 87, w_ / 2)
    img_gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    # detect circles in the image
    circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, 1.2, 100,minRadius=50,maxRadius=75)
    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        is_has_triangle_inside = False
        for (x, y, r) in circles:  
            if x >= threshold_pos_x[0] - 2*r and x <= threshold_pos_x[0] + 2*r:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                cropped_image = input_image.copy()[y-r:y+r,x-r:x+r].copy()
                
                # cv2.imshow('tri',cropped_image)
                # cv2.waitKey(0)
                if 0 in cropped_image.shape: continue
                list_triangle = find_triangle_twitter(cropped_image)
                for triangle in list_triangle:
                    x_tri = triangle.ravel()[0]
                    y_tri = triangle.ravel()[1] 
                    triangle[:,:,::2] += x - r
                    triangle[:,:,1::2] += y - r 
                    cv2.drawContours(output, [triangle], -1, (0,255,0), 3)
                    cv2.putText(output, "Play btn", (x_tri + x -r , y_tri + y -r ), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,255,0))
                    is_has_triangle_inside = True 
        if is_has_triangle_inside: return True
    return False

def scroll_by_screen(driver):
    actions = TouchAction(driver)  
    size = driver.get_window_size()
    padding = 500
    max_height = size['height'] - padding
    max_width = size['width'] - padding
    
    middle_width = round(max_width / 2)
    middle_height = round(max_height / 2)
 
    for i in range(0, 20): 
        image_path = get_screen_shoot(driver,i)
        is_collect_image, type_ads, dst_path = handle_collect(image_path)
        if is_collect_image:
            log('Type: {} - {}'.format(type_ads.upper(), dst_path.replace('/Users/genkisystem/Desktop/ISSO_2/class_ocr/','')))          
            # is_carousel = check_is_carousel(driver)
            # if is_carousel:
            #     # save images in carousel
            #     log('This is carousel')
            # else:
            is_video = check_is_has_play_btn(dst_path)
            if is_video:
                # handle play and record video
                log("This is video")
                # save video 
                # video_path = '{}.mp4'.format(image_path.split('.')[0]) 
                # record_video(driver, video_path) 
            else:
                # handle save images
                log("This is image")
        scroll_down(driver)

# Android environment
import unittest
import base64
import io
from PIL import Image 
import time

desired_caps = dict(
{
   "platformName":"Android",
   "platformVersion":"12",
   "automationName":"uiautomator2",
   "deviceName":"Android Emulator",
   "newCommandTimeout":180,
   "browserstack.appStoreConfiguration":"{\"username\":\"duytnb2608.promote@gmail.com\", \"password\":\"Mushroomzz99--\"}"
})

driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

import uuid
# get_activity(driver) 
# scroll_by_screen(driver)  
# scroll_to_right(driver)
record_video(driver, './class_ocr/temp/abc.mp4')