import cv2, dlib, sys
import numpy as np

scaler = 0.7

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# load video
#cap = cv2.VideoCapture('IU_demo.mp4') # 동영상
cap = cv2.VideoCapture(0)   # 웹캠

face_roi = []
face_sizes = []
img_count = 0

while True:
    ret, img = cap.read()
    if not ret:
        break

    img = cv2.resize(img,(int(img.shape[1] * scaler),int(img.shape[0] *scaler)))
    ori = img.copy()

    # detect faces
    faces = detector(img)
    try:
        face = faces[0]
        print(face)
        # 얼굴 특징점 추출
        dlib_shape = predictor(img,face)
        shape_2d = np.array([[p.x,p.y] for p in dlib_shape.parts()])

        # compute center and boundaries of face
        top_left = np.min(shape_2d, axis=0) # 얼굴의 좌상단
        bottom_right = np.max(shape_2d, axis=0) # 얼굴의 우하단 구하기

        face_size = max(bottom_right - top_left)

        # 얼굴의 중심점 구하기
        center_x, center_y = np.mean(shape_2d, axis=0).astype(np.int)    # 소수점일 수도 있으니 정수형으로 변환

        # 서버로 보낼 사진 추출
        img_count+=1
        #imgname = './img/test'+str(img_count)+'.png'    # img 저장 위치+ 이름
        #imgname = '../age_gender/testimg/'+str(img_count)+'.jpg'
        imgname = './img/'+str(img_count)+'.jpg'
        cv2.imwrite(imgname,img)

        # visualize
        img = cv2.rectangle(img, pt1=(face.left(),face.top()),pt2=(face.right(),face.bottom()),color=(255,255,255),
                            thickness=2,lineType=cv2.LINE_AA)

        # 68개의 특징점을 그리기
        for s in shape_2d:
            cv2.circle(img, center=tuple(s), radius=1,color=(255,255,255), thickness=2,lineType =cv2.LINE_AA)

        # 좌상단, 우하단 특징점 파란색으로 표시
        cv2.circle(img,center=tuple(top_left),radius=1,color=(255,0,0),thickness=2,lineType=cv2.LINE_AA)
        cv2.circle(img, center=tuple(bottom_right), radius=1, color=(255, 0, 0), thickness=2, lineType=cv2.LINE_AA)

        cv2.circle(img, center=tuple((center_x,center_y)), radius=1, color=(0, 0, 255), thickness=2, lineType=cv2.LINE_AA)

    except IndexError:
        pass
    cv2.imshow('img',img)
    # cv2.imshow('result',result)
    cv2.waitKey(1)