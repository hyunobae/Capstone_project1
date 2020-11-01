import cv2, dlib, sys
import numpy as np
import socket
import argparse
import threading
import sys
import time
import os
from os.path import exists


port = 10000
host = "192.168.43.104"

def getFileSize(Filename):
    filesize = os.path.getsize(Filename)
    print(filesize)
    return str(filesize)

scaler = 0.7

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# load video
cap = cv2.VideoCapture(0)

face_roi = []
face_sizes = []
img_count = 0


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host,port))
print("connect sucess!")


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
        dlib_shape = predictor(img,face)
        shape_2d = np.array([[p.x,p.y] for p in dlib_shape.parts()])

        top_left = np.min(shape_2d, axis=0)
        bottom_right = np.max(shape_2d, axis=0)

        face_size = max(bottom_right - top_left)

        center_x, center_y = np.mean(shape_2d, axis=0).astype(np.int)

        img_count+=1
        imgname = './img/'+str(img_count)+'.jpg'
        cv2.imwrite(imgname,img)
        fd = open(imgname,'rb')
        client_socket.send(getFileSize(imgname).encode())
        client_socket.recv(32)
        b = fd.read()
        client_socket.send(b)

        img = cv2.rectangle(img, pt1=(face.left(),face.top()),pt2=(face.right(),face.bottom()),color=(255,255,255),
                            thickness=2,lineType=cv2.LINE_AA)

        for s in shape_2d:
            cv2.circle(img, center=tuple(s), radius=1,color=(255,255,255), thickness=2,lineType =cv2.LINE_AA)

        cv2.circle(img,center=tuple(top_left),radius=1,color=(255,0,0),thickness=2,lineType=cv2.LINE_AA)
        cv2.circle(img, center=tuple(bottom_right), radius=1, color=(255, 0, 0), thickness=2, lineType=cv2.LINE_AA)

        cv2.circle(img, center=tuple((center_x,center_y)), radius=1, color=(0, 0, 255), thickness=2, lineType=cv2.LINE_AA)

    except IndexError:
        pass
    cv2.imshow('img',img)
    # cv2.imshow('result',result)
    cv2.waitKey(1)

client_socket.close()
