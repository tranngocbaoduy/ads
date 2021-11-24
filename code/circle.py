import cv2
import numpy as np
import glob 

from skimage.metrics import structural_similarity as ssim

def find_triangle(input_image):  
    #convert image into greyscale mode
    list_triangle = []
    gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

    # cv2.imshow('gray_image',gray_image)
    # cv2.waitKey(0)
    #find threshold of the image
    _, thrash = cv2.threshold(gray_image, 230, 255, cv2.THRESH_BINARY) 
    # cv2.imshow('thrash',thrash)
    # cv2.waitKey(0)
    contours, _ = cv2.findContours(thrash, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # print('contours',contours)
    for contour in contours:
        # check area of contour must be in range 1500 ~ 2000
        if cv2.contourArea(contour) < 1500 or cv2.contourArea(contour) > 2000: continue
        # print('arre',0.1*cv2.arcLength(contour, True), cv2.contourArea(contour))
        shape = cv2.approxPolyDP(contour, 0.1*cv2.arcLength(contour, True), True)
        x_cor = shape.ravel()[0]
        y_cor = shape.ravel()[1]

        #For triangle
        if len(shape) ==3:
            list_triangle.append(shape)
    return list_triangle

def check_is_has_play_btn_fb(path):
    input_image = cv2.imread(path)
    output = input_image.copy()
    img_gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    # detect circles in the image
    circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, 1.2, 100,minRadius=70,maxRadius=85)
    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        is_has_triangle_inside = False
        for (x, y, r) in circles:  
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            cropped_image = input_image.copy()[y-r:y+r,x-r:x+r].copy()
            
            cv2.imshow('tri',cropped_image)
            cv2.waitKey(0)
            if 0 in cropped_image.shape: continue
            list_triangle = find_triangle(cropped_image)
            for triangle in list_triangle:
                x_tri = triangle.ravel()[0]
                y_tri = triangle.ravel()[1] 
                triangle[:,:,::2] += x - r
                triangle[:,:,1::2] += y - r 
                cv2.drawContours(output, [triangle], -1, (0,255,0), 3)
                cv2.putText(output, "Play btn", (x_tri + x -r , y_tri + y -r ), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,255,0))
                is_has_triangle_inside = True
        # show the output image 
        cv2.imshow("output", np.hstack([input_image, output]))
        cv2.waitKey(0)
        if is_has_triangle_inside: return 1
    return 0



def find_triangle_twitter(input_image):  
    #convert image into greyscale mode
    list_triangle = []
    gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

    # cv2.imshow('gray_image',gray_image)
    # cv2.waitKey(0)
    #find threshold of the image
    _, thrash = cv2.threshold(gray_image, 230, 255, cv2.THRESH_BINARY) 
    # cv2.imshow('thrash',thrash)
    # cv2.waitKey(0)
    contours, _ = cv2.findContours(thrash, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # print('contours',contours)
    for contour in contours:
        # check area of contour must be in range 750 ~ 800
        if cv2.contourArea(contour) < 750 or cv2.contourArea(contour) > 800: continue
        # print('arre',0.1*cv2.arcLength(contour, True), cv2.contourArea(contour))
        shape = cv2.approxPolyDP(contour, 0.1*cv2.arcLength(contour, True), True)
        x_cor = shape.ravel()[0]
        y_cor = shape.ravel()[1]

        #For triangle
        if len(shape) ==3:
            list_triangle.append(shape)
    return list_triangle

def check_is_has_play_btn_twitter(path):
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
            print('threshold_pos_x',threshold_pos_x, x, threshold_pos_x[0] - r, threshold_pos_x[0] + r)
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
                print('triangle',len(list_triangle))
                for triangle in list_triangle:
                    x_tri = triangle.ravel()[0]
                    y_tri = triangle.ravel()[1] 
                    triangle[:,:,::2] += x - r
                    triangle[:,:,1::2] += y - r 
                    cv2.drawContours(output, [triangle], -1, (0,255,0), 3)
                    cv2.putText(output, "Play btn", (x_tri + x -r , y_tri + y -r ), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,255,0))
                    is_has_triangle_inside = True
        # show the output image 
        cv2.imshow("output", np.hstack([input_image, output]))
        cv2.waitKey(0)
        if is_has_triangle_inside: return 1
    return 0

def compare_image(img1, img2):
    (score, diff) = ssim(img1, img2, full=True)
    return score, diff

def check_is_has_dots_ins(path):
    method = cv2.TM_SQDIFF_NORMED
    list_image_path = glob.glob("./assets/icon/ins_simple/*.png")
    print('list_image_path', len(list_image_path))
    output_image = cv2.imread(path)
    input_image = output_image.copy()
    threshold = .28
    h_, w_ = input_image.shape[:-1] 
    threshold_pos_y = h_ / 2
    threshold_pos_x = (w_ / 2 - 87, w_ / 2)
    is_found = 0
    position_image = tuple()
    # Read the images from the file
    for icon_path in list_image_path:
        small_image = cv2.imread(icon_path)
        small_image_gray = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)
        h, w = small_image.shape[:-1]
        result = cv2.matchTemplate(small_image, output_image, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        for position in zip(*loc[::-1]):  # Switch collumns and rows
            if 'shop' in icon_path: 
                if position[0] < threshold_pos_x[0] and position[1] > threshold_pos_y :
                    cropped_image = input_image.copy()[position[1]:position[1]+h,position[0]:position[0]+w].copy()
                    cropped_image_gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
                    score, diff = compare_image(cropped_image_gray, small_image_gray)
                    if score < 0.7: continue

                    is_found = True
                    position_image = (position[0], position[0] + w, position[1], position[1] + h) 
                    cv2.rectangle(output_image, position, (position[0] + w, position[1] + h), (0, 255, 0), 2)
            else: 
                
                if position[1] > threshold_pos_y and position[0] > threshold_pos_x[0] and position[0] < threshold_pos_x[1] and position[1] < h_ - 300:
                    cropped_image = input_image.copy()[position[1]:position[1]+h,position[0]:position[0]+w].copy()
                    cropped_image_gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
                    score, diff = compare_image(cropped_image_gray, small_image_gray)
                    print('icon_path',icon_path)
                    if '3-dot-1' in icon_path:
                        print('icon', score)
                    if score < 0.75: continue

                    is_found = True
                    position_image = (position[0], position[0] + w, position[1], position[1] + h) 
                    cv2.rectangle(output_image, position, (position[0] + w, position[1] + h), (0, 0, 255), 2)
            if is_found: break
        if is_found: break
    cv2.imshow("output", np.hstack([input_image, output_image]))
    cv2.waitKey(0)
    if is_found: return True, position_image
    return False, ()

app_name = 'twitter'

if app_name == 'facebook':
    list_image_path = glob.glob("./assets/detect-example/fb/*.png")
    count_true = 0
    error_image = []
    for path in list_image_path:
        # Load image:
        if 'tee.png' in path :
            is_has_play_btn = check_is_has_play_btn_fb(path)
            if is_has_play_btn == 0:
                error_image.append(path)
            count_true += is_has_play_btn

    print("Found {}/{} circle".format(count_true, len(list_image_path)))
    print("Not found",error_image)

if app_name == 'ins':
    is_has_dots, position = check_is_has_dots_ins('assets/detect-example/ins/image-10.png')
    print(is_has_dots, position)


if app_name == 'twitter':
    list_image_path = glob.glob("./assets/detect-example/twitter/*.png")
    count_true = 0
    error_image = []
    for path in list_image_path:
        # Load image: 
        is_has_play_btn = check_is_has_play_btn_twitter(path)
        if is_has_play_btn == 0:
            error_image.append(path)
        count_true += is_has_play_btn
    print("Found {}/{} circle".format(count_true, len(list_image_path)))
    print("Not found",error_image)

