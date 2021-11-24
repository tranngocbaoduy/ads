import cv2

# method = cv2.TM_CCOEFF
method = cv2.TM_SQDIFF_NORMED

# Read the images from the file
small_image = cv2.imread('./assets/play-btn-2.png')
small_image = cv2.bitwise_not(small_image)

gray_small_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)
blur_small_image = cv2.GaussianBlur(gray_small_image, (3,3), 0)
cv2.imshow('3',blur_small_image)
cv2.waitKey(0)
edges_small_image = cv2.Canny(image=gray_small_image, threshold1=0, threshold2=350)

cv2.imshow('1',edges_small_image)
cv2.waitKey(0)

large_image = cv2.imread('./assets/large_image_1.png')

gray_large_image = cv2.cvtColor(large_image, cv2.COLOR_BGR2GRAY)
blur_large_image = cv2.GaussianBlur(gray_large_image, (3,3), 0)
edges_large_image = cv2.Canny(image=blur_large_image, threshold1=50, threshold2=200)

cv2.imshow('2',edges_large_image)
cv2.waitKey(0)

result = cv2.matchTemplate( edges_large_image,edges_small_image, method)

# We want the minimum squared difference
mn,_,mnLoc,_ = cv2.minMaxLoc(result)

# Draw the rectangle:
# Extract the coordinates of our best match
MPx,MPy = mnLoc 
print(MPx, MPy)
# Step 2: Get the size of the template. This is the same size as the match.
trows,tcols = small_image.shape[:2]

# Step 3: Draw the rectangle on large_image
cv2.rectangle(large_image, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)

# Display the original image with the rectangle around the match.
cv2.imshow('output',large_image)

# The image is only displayed if we call this
cv2.waitKey(0)