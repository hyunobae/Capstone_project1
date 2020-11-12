import socket
import argparse
import threading
import time
import os
import shutil

host = ''
port = 10000
user_list = []
notice_flag = 0

def msg_func(msg):
    print(msg)
    for con in user_list.values():
        try:
            con.send(msg.encode('utf-8'))
        except:
            print("연결이 비 정상적으로 종료된 소켓 발견")
            exit()


def handle_receive(client_socket, addr):
    print("connect with " + str(addr))
    count = 0
    string = str(addr)
    #ip와 socketnum 얻어오기

    dir_name = os.getcwd()
    dir_name += "/Client" +str(user_list.index(addr))
    #받아온 client별로 폴더 이름 지정

    try:
        shutil.rmtree(dir_name) #디렉토리가 존재하면 삭제
    except Exception as e:
        print(dir_name)
    
    os.makedirs(dir_name)#디렉토리 생성
    
    while 1:
        file_length = client_socket.recv(1024)
        #file 크기를 받는 과정
        client_socket.send("str".encode())
        file_length = file_length.decode()
        #file_length에는 server가 받아올 file 크기가 저장됨
        #print(file_length)
        if not file_length:
            break

        length = 0
        data = []
        #file을 붙이는 과정
        while 1:
            d = client_socket.recv(4096)
            data.append(d)
            #data에 4096바이트씩 받아오면서 연결해줌
            length += len(d)
            #print(length)
            if int(length) == int(file_length):
                #print('break')
                break

        stri = dir_name + "/" + string + str(count) + ".jpg" #jpg 파일 생성
        count+=1
        #print(str(addr) + " : " + stri)
        with open(stri, 'wb') as f:
            for a in data:
                f.write(a)

    print("disconnect with " + str(addr))
    user_list.remove(addr)

def handle_notice(client_socket, addr):
    pass


def accept_func():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #포트를 사용 중 일때 에러를 해결하기 위한 구문
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))

    server_socket.listen(5)
    #최대 5개 가능
    
    while 1:
        client_socket, addr = server_socket.accept()

        user_list.append(addr)

        #accept()함수로 입력만 받아주고 이후 알고리즘은 핸들러에게 맡긴다.
        notice_thread = threading.Thread(target=handle_notice, args=(client_socket, addr))
        notice_thread.daemon = True
        notice_thread.start()

        receive_thread = threading.Thread(target=handle_receive, args=(client_socket, addr))
        receive_thread.daemon = True
        receive_thread.start()


if __name__ == '__main__':
    accept_func()
