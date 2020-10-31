import cv2
import numpy as np
 
image = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('files/haarcascade_frontalface_default.xml')
 
while True:
    ret, frame = image.read()
    image_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
    faces = face_cascade.detectMultiScale(image_gray, 1.3, 5)
 
    for (x,y,w,h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = image_gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
    cv2.imshow('img',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.waitKey(0)

image.release()
cv2.destroyAllWindows()

