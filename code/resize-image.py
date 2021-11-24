import cv2
 
img = cv2.imread('./assets/play-btn-icon-x1.png', cv2.IMREAD_UNCHANGED)
 
print('Original Dimensions : ',img.shape) 
dim = (148, 148)
  
# resize image
resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
print('Resized Dimensions : ',resized.shape)

cv2.imshow("Resized image", resized)
cv2.waitKey(0)
cv2.imwrite('./assets/resize-play-btn-icon-x1.png', resized)
cv2.destroyAllWindows()