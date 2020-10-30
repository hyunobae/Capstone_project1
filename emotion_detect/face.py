import cv2
import numpy as np
 
# 테스트 이미지 불러오기
image = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('files/haarcascade_frontalface_default.xml')
 
# RGB -> Gray로 변환
# 얼굴 찾기 위해 그레이스케일로 학습되어 있기때문에 맞춰줘야 한다.
while True:
    ret, frame = image.read()
    image_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
    faces = face_cascade.detectMultiScale(image_gray, 1.3, 5)
 
# 얼굴 검출되었다면 좌표 정보를 리턴받는데, 없으면 오류를 뿜을 수 있음. 
    for (x,y,w,h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2) # 원본 영상에 위치 표시
        roi_gray = image_gray[y:y+h, x:x+w] # roi 생성
        roi_color = frame[y:y+h, x:x+w] # roi
    cv2.imshow('img',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.waitKey(0)

image.release()
cv2.destroyAllWindows()

