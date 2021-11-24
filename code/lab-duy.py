import cv2
import base64
import numpy as np
from skimage.metrics import structural_similarity as ssim


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

video_path_1 = '/Users/genkisystem/Desktop/ISSO_2/class_ocr/0-12f3ff14-3b5e-4e60-910b-71df31ec3365.mp4'
video_path_2 = '/Users/genkisystem/Desktop/ISSO_2/class_ocr/3-42275dcb-ce5d-48d4-861f-4141a32310ad.mp4'


def save_image(image, path):
    status = cv2.imwrite(path,image)

def save_frame_to_image(frames):
    for index, frame in enumerate(frames):
        save_image(frame, '/Users/genkisystem/Desktop/ISSO_2/class_ocr/test/image_{}.png'.format(str(index)))

def compare_image(img1, img2):
    (score, diff) = ssim(img1, img2, full=True)
    return score, diff

def check_is_likely(frames):
    first_image = cv2.cvtColor(frames[0] , cv2.COLOR_BGR2GRAY)
    for frame in frames[1:]:
        image_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Compute SSIM between two images
        score, diff = compare_image(first_image, image_gray):
        print('score', score)
         

frames = footage_to_frame(video_path_1)

print(len(frames))
check_is_likely(frames)
# save_frame_to_image(frames)