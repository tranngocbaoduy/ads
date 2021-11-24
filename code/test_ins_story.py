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
APP_PATH = "ins"
CATEGORY_ADS_PATH = "sponsor"
CATEGORY_SUGGEST_PATH = "suggest_for_you"
CATEGORY_PRODUCT_PATH = "product"

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

def zoom(img, zoom_factor=2):
    return cv2.resize(img, None, fx=zoom_factor, fy=zoom_factor) 

def get_text_from_image(image_path, lang='jpn+eng'):

    img = cv2.imread(image_path)
    h_, w_ = img.shape[:-1]  
    cropped_image = img.copy()[60:380, 0: int(w_/3*2)]
    # cropped_image = img.copy()[50:300, 0:int(w_/2)]
    gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    _, thrash = cv2.threshold(gray_image, 230, 255, cv2.THRESH_BINARY)  
    thrasss = cv2.bitwise_not(thrash)
    
    zoom_img = zoom(thrasss, zoom_factor=1.2) 
    # cv2.imshow('threas',zoom_img)
    # cv2.waitKey(0)
    text = pytesseract.image_to_string(zoom_img, lang)
    return text

def is_collect(paragraph): 
    allow_texts = ['ショップを見る', 'Sponsored', '広告', 'おすすめ']
    for allow_text in allow_texts:
        if allow_text in paragraph: return True
    return False

def category_text(text):
    if 'おすすめ' in text: return "suggest"
    if '広告' in text or 'Sponsored' in text: return "ads"
    if 'ショップを見る' in text: return "product"
    return "ads"

def handle_collect(image_path):
    lang = 'jpn+eng'
    # lang = 'en'
    text = get_text_from_image(image_path,lang=lang) 
    is_collect_image = is_collect(text.strip())
    if is_collect_image:
        type_ads = category_text(text)

        if type_ads == 'ads': dst_path = os.path.join(MAIN_PATH, 'category',APP_PATH, run_time_iso_date,CATEGORY_ADS_PATH)
        if type_ads == 'suggest': dst_path = os.path.join(MAIN_PATH, 'category',APP_PATH, run_time_iso_date, CATEGORY_SUGGEST_PATH)
        if type_ads == 'product': dst_path = os.path.join(MAIN_PATH, 'category',APP_PATH, run_time_iso_date, CATEGORY_PRODUCT_PATH)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        head, tail = os.path.split(image_path)
        dst_path = os.path.join(dst_path, tail)
        copy_file(image_path, dst_path) 
        return True, type_ads, dst_path, text 
    return False, None, "", text


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
    time.sleep(10)
    video = driver.stop_recording_screen() 
    print('stop record')
    
    fh = open("{}".format(path), "wb")
    fh.write(base64.b64decode(video))
    print('save record')
    time.sleep(5) 
    fh.close()

def handle_save_video(path, video):
    # print('handle_save_video')
    fh = open("{}".format(path), "wb")
    fh.write(base64.b64decode(video))
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
    header_height = 350
    driver.swipe(middle_width, middle_height , middle_width, middle_height - top + header_height, 3000)  
     
def scroll_to_right(driver): 
    time.sleep(0.2)
    size = driver.get_window_size()
    padding = 500
    max_height = size['height'] - padding
    max_width = size['width'] - padding
    
    middle_width = round(max_width / 2)
    middle_height = round(max_height / 2) 

    driver.swipe(middle_width, middle_height , -middle_width, middle_height, 1500)  
    time.sleep(0.2)

def scroll_to_left(driver): 
    time.sleep(0.2)
    size = driver.get_window_size()
    padding = 500
    max_height = size['height'] - padding
    max_width = size['width'] - padding
    
    middle_width = round(max_width / 2)
    middle_height = round(max_height / 2) 

    driver.swipe(middle_width, middle_height , 2*middle_width, middle_height, 1500)  
    time.sleep(0.2)

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

from difflib import SequenceMatcher 

def check_is_finish_story(driver, init_text):
    is_continue = True
    count = 0
    while is_continue and count < 30:
        image_path = get_screen_shoot(driver,path="class_ocr/temp/temp3.png") 
        text = get_text_from_image(image_path,lang='jpn+eng')
        similarity = SequenceMatcher(None, text, init_text)
        if(similarity.ratio() < 0.6):
            is_continue = False
        count +=1
    return True

def handle_record_video(driver, init_text, dst_path):
    scroll_to_left(driver) 
    driver.start_recording_screen() 
    scroll_to_right(driver) 

    time.sleep(3) 
    check_is_finish_story(driver, init_text) 
    video = driver.stop_recording_screen()  
    handle_save_video(dst_path.replace('png','mp4'),video)
    time.sleep(2)

def handle_story(driver):
    actions = TouchAction(driver)  
    size = driver.get_window_size()
    padding = 500
    max_height = size['height'] - padding
    max_width = size['width'] - padding
    
    middle_width = round(max_width / 2)
    middle_height = round(max_height / 2)
 
    for i in range(0, 20): 
        image_path = get_screen_shoot(driver,i) 
        is_collect_image, type_ads, dst_path, init_text = handle_collect(image_path)
        if is_collect_image:
            log('Type: {}. Collect story: {}'.format(type_ads, dst_path.replace('/Users/genkisystem/Desktop/ISSO_2/class_ocr/category/','')))
            handle_record_video(driver, init_text, dst_path) 
            log('Save video at {}'.format(dst_path.replace('png','mp4').replace('/Users/genkisystem/Desktop/ISSO_2/class_ocr/category/','')))

        scroll_to_right(driver)


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
handle_story(driver)  
