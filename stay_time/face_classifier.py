# 원본 코드
#!/usr/bin/env python3
#밑의 코드에서 라즈베리파이 숫자 수정하고 돌리기
#실행방법 -> terminal -> python face_classifier.py 0 -t 0.35 -d
import errno

from person_db import Person
from person_db import Face
from person_db import PersonDB
import face_recognition
import numpy as np
#import datetime
from datetime import datetime
#import datetime
import cv2


class FaceClassifier():
    def __init__(self, threshold, ratio):
        self.similarity_threshold = threshold
        self.ratio = ratio

    def get_face_image(self, frame, box):
        img_height, img_width = frame.shape[:2]
        (box_top, box_right, box_bottom, box_left) = box
        box_width = box_right - box_left
        box_height = box_bottom - box_top
        crop_top = max(box_top - box_height, 0)
        pad_top = -min(box_top - box_height, 0)
        crop_bottom = min(box_bottom + box_height, img_height - 1)
        pad_bottom = max(box_bottom + box_height - img_height, 0)
        crop_left = max(box_left - box_width, 0)
        pad_left = -min(box_left - box_width, 0)
        crop_right = min(box_right + box_width, img_width - 1)
        pad_right = max(box_right + box_width - img_width, 0)
        face_image = frame[crop_top:crop_bottom, crop_left:crop_right]
        if (pad_top == 0 and pad_bottom == 0):
            if (pad_left == 0 and pad_right == 0):
                return face_image
        padded = cv2.copyMakeBorder(face_image, pad_top, pad_bottom,
                                    pad_left, pad_right, cv2.BORDER_CONSTANT)
        return padded

    # return list of dlib.rectangle
    def locate_faces(self, frame):
        #start_time = time.time()
        if self.ratio == 1.0:
            rgb = frame[:, :, ::-1]
        else:
            small_frame = cv2.resize(frame, (0, 0), fx=self.ratio, fy=self.ratio)
            rgb = small_frame[:, :, ::-1]
        boxes = face_recognition.face_locations(rgb)
        #elapsed_time = time.time() - start_time
        #print("locate_faces takes %.3f seconds" % elapsed_time)
        if self.ratio == 1.0:
            return boxes
        boxes_org_size = []
        for box in boxes:
            (top, right, bottom, left) = box
            left = int(left / ratio)
            right = int(right / ratio)
            top = int(top / ratio)
            bottom = int(bottom / ratio)
            box_org_size = (top, right, bottom, left)
            boxes_org_size.append(box_org_size)
        return boxes_org_size

    def detect_faces(self, frame,frame_name):
        boxes = self.locate_faces(frame)
        if len(boxes) == 0:
            return []

        # faces found
        faces = []
        now = datetime.now()
        str_ms = now.strftime('%Y%m%d_%H%M%S.%f')[:-3] + '-'
        encodings = face_recognition.face_encodings(frame, boxes)
        for i, box in enumerate(boxes):
            face_image = self.get_face_image(frame, box)
            #face = Face(str_ms + str(i) + ".png", face_image, encodings[i])
            #face = Face(frame_name + ".png",face_image,encodings[i])
            face = Face(frame_name,face_image,encodings[i])
            face.location = box
            faces.append(face)
        return faces

    def compare_with_known_persons(self, face, persons):
        if len(persons) == 0:
            return None

        # see if the face is a match for the faces of known person
        encodings = [person.encoding for person in persons]
        distances = face_recognition.face_distance(encodings, face.encoding)
        index = np.argmin(distances)
        min_value = distances[index]
        if min_value < self.similarity_threshold:
            # face of known person
            persons[index].add_face(face)
            # re-calculate encoding
            persons[index].calculate_average_encoding()
            face.name = persons[index].name
            return persons[index]

    def compare_with_unknown_faces(self, face, unknown_faces):
        if len(unknown_faces) == 0:
            # this is the first face
            unknown_faces.append(face)
            face.name = "unknown"
            return

        encodings = [face.encoding for face in unknown_faces]
        distances = face_recognition.face_distance(encodings, face.encoding)
        index = np.argmin(distances)
        min_value = distances[index]
        if min_value < self.similarity_threshold:
            # two faces are similar - create new person with two faces
            person = Person()
            newly_known_face = unknown_faces.pop(index)
            person.add_face(newly_known_face)
            person.add_face(face)
            person.calculate_average_encoding()
            face.name = person.name
            newly_known_face.name = person.name
            return person
        else:
            # unknown face
            unknown_faces.append(face)
            face.name = "unknown"
            return None

    def draw_name(self, frame, face):
        color = (0, 0, 255)
        thickness = 2
        (top, right, bottom, left) = face.location

        # draw box
        width = 20
        if width > (right - left) // 3:
            width = (right - left) // 3
        height = 20
        if height > (bottom - top) // 3:
            height = (bottom - top) // 3
        cv2.line(frame, (left, top), (left+width, top), color, thickness)
        cv2.line(frame, (right, top), (right-width, top), color, thickness)
        cv2.line(frame, (left, bottom), (left+width, bottom), color, thickness)
        cv2.line(frame, (right, bottom), (right-width, bottom), color, thickness)
        cv2.line(frame, (left, top), (left, top+height), color, thickness)
        cv2.line(frame, (right, top), (right, top+height), color, thickness)
        cv2.line(frame, (left, bottom), (left, bottom-height), color, thickness)
        cv2.line(frame, (right, bottom), (right, bottom-height), color, thickness)

        # draw name
        #cv2.rectangle(frame, (left, bottom + 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, face.name, (left + 6, bottom + 30), font, 1.0,
                    (255, 255, 255), 1)


if __name__ == '__main__':
    import argparse
    import signal
    import time
    import os

    ap = argparse.ArgumentParser()
    ap.add_argument("inputfile",
                    help="video file to detect or '0' to detect from web cam")
    ap.add_argument("-t", "--threshold", default=0.44, type=float,
                    help="threshold of the similarity (default=0.44)")
    ap.add_argument("-S", "--seconds", default=1, type=float,
                    help="seconds between capture")
    ap.add_argument("-s", "--stop", default=0, type=int,
                    help="stop detecting after # seconds")
    ap.add_argument("-k", "--skip", default=0, type=int,
                    help="skip detecting for # seconds from the start")
    ap.add_argument("-d", "--display", action='store_true',
                    help="display the frame in real time")
    ap.add_argument("-c", "--capture", type=str,
                    help="save the frames with face in the CAPTURE directory")
    ap.add_argument("-r", "--resize-ratio", default=1.0, type=float,
                    help="resize the frame to process (less time, less accuracy)")
    args = ap.parse_args()

    src_file = args.inputfile

    # 각 라즈베리파이에서 받아온 사진들은 total에 저장되었다고 가정(나중에 파일이름 수정)
    # ex>
    # 라즈베리파이1에서 받아온 파일명 -> client1일 경우 밑의 total_img = './client1'로 수정
    # 라파가 여러개 일 경우 이러한 total_img를 계속 이름을 수정해줘야함
    # 그리하여 frame_img를 계속 바꾸고 그걸 돌리는 느낌
    # 즉, 여러개의 라파의 각각의 체류시간을 구하기 위해서는 이 아랫부분을 for 문으로 감싸 라파 갯수만큼 실행시키면 된다.

    # 각 라즈베리파이의 체류시간 분석에 대한 정보를 담을 directory(stay time) 생성
    try:
        if not (os.path.isdir('stay_time')):
            os.makedirs(os.path.join('stay_time'))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise

    #num_of_Raspberry = int(input())
    for q in range(2):  # range(~~~) -> client 수
    #for q in range(num_of_Raspberry):
        if src_file == "0":
            total_img = './client'+str(q)
            frame_img = os.listdir(total_img)
            frame_img.sort()
            src_file = './client'+str(q) + '/' + frame_img[0]

        src = cv2.VideoCapture(src_file)

        if not src.isOpened():
            print("cannot open inputfile", src_file)
            exit(1)

        frame_width = src.get(cv2.CAP_PROP_FRAME_WIDTH)
        frame_height = src.get(cv2.CAP_PROP_FRAME_HEIGHT)
        frame_rate = src.get(5)
        frames_between_capture = int(round(frame_rate * args.seconds))

        print("source", args.inputfile)
        print("original: %dx%d, %f frame/sec" % (src.get(3), src.get(4), frame_rate))
        ratio = float(args.resize_ratio)
        if ratio != 1.0:
            s = "RESIZE_RATIO: " + args.resize_ratio
            s += " -> %dx%d" % (int(src.get(3) * ratio), int(src.get(4) * ratio))
            print(s)
        print("process every %d frame" % frames_between_capture)
        print("similarity shreshold:", args.threshold)
        if args.stop > 0:
            print("Detecting will be stopped after %d second." % args.stop)

        # load person DB
        result_dir = "result" + str(q)
        pdb = PersonDB()
        pdb.load_db(result_dir)
        pdb.print_persons()

        # prepare capture directory
        num_capture = 0
        if args.capture:
            print("Captured frames are saved in '%s' directory." % args.capture)
            if not os.path.isdir(args.capture):
                os.mkdir(args.capture)

        # set SIGINT (^C) handler
        def signal_handler(sig, frame):
            global running
            running = False
        prev_handler = signal.signal(signal.SIGINT, signal_handler)
        if args.display:
            print("Press q to stop detecting...")
        else:
            print("Press ^C to stop detecting...")

        #fc = FaceClassifier(args.threshold, ratio)
        fc = FaceClassifier(0.35, 1.0)
        frame_id = 0
        running = True

        total_start_time = time.time()
        frame_cnt = 0
        while running:
            if len(frame_img) == frame_cnt:
                break
            src_file = './client' +str(q)+'/'+ frame_img[frame_cnt]
            src = cv2.VideoCapture(src_file)

            ret, frame = src.read()
            if frame is None:
                print('hi')
                break

            frame_id += 1
            #if frame_id % frames_between_capture != 0:
    #            continue

            seconds = round(frame_id / frame_rate, 3)
            if args.stop > 0 and seconds > args.stop:
                break
            if seconds < args.skip:
                continue

            start_time = time.time()

            # this is core
            # 2020 11 15
            #faces = fc.detect_faces(frame)
            faces = fc.detect_faces(frame,frame_img[frame_cnt])
            frame_cnt += 1
            for face in faces:
                person = fc.compare_with_known_persons(face, pdb.persons)
                if person:
                    continue
                person = fc.compare_with_unknown_faces(face, pdb.unknown.faces)
                if person:
                    pdb.persons.append(person)

            if args.display or args.capture:
                for face in faces:
                    fc.draw_name(frame, face)
                if args.capture and len(faces) > 0:
                    now = datetime.now()
                    filename = now.strftime('%Y%m%d_%H%M%S.%f')[:-3] + '.png'
                    pathname = os.path.join(args.capture, filename)
                    #cv2.imwrite(pathname, frame)
                    cv2.imwrite(frame_img[frame_cnt-1])
                    num_capture += 1
                # if args.display:
                #     cv2.imshow("Frame", frame)
                #     # imshow always works with waitKey
                #     key = cv2.waitKey(1) & 0xFF
                #     # if the `q` key was pressed, break from the loop
                #     if key == ord("q"):
                #         running = False

            elapsed_time = time.time() - start_time

            s = "\rframe " + str(frame_id)
            s += " @ time %.3f" % seconds
            s += " takes %.3f second" % elapsed_time
            s += ", %d new faces" % len(faces)
            s += " -> " + repr(pdb)
            if num_capture > 0:
                s += ", %d captures" % num_capture
            print(s, end="    ")

        # restore SIGINT (^C) handler
        signal.signal(signal.SIGINT, prev_handler)
        running = False
        src.release()
        total_elapsed_time = time.time() - total_start_time
        print()
        print("total elapsed time: %.3f second" % total_elapsed_time)

        pdb.save_db(result_dir)
        pdb.print_persons()

        # 체류시간 계산하기
        path_person_dir = './result' + str(q) + '/'

        temp = os.listdir(path_person_dir)
        dir_person = []
        f = open('./stay_time/client'+str(q)+".txt", 'w')   #체류시간 저장할 txt 이름

        # person 디렉터리 이름 가져오기 -> dir_person에 저장
        for i in range(len(temp)):
            if temp[i].startswith('person_'):
                dir_person.append(temp[i])
        # print(dir_person)

        #
        print("client"+str(q))
        f.write("client"+str(q)+"\n")

        for j in range(len(dir_person)):
            # path_dir = './result/person_01'
            path_dir = './result' +str(q)+'/'+ dir_person[j]
            file_list = os.listdir(path_dir)
            #print(file_list)

            file_list.sort()

            flag = 0
            start_time = 0
            now_time = 0
            print(dir_person[j])
            f.write(dir_person[j]+"\n")
            for i in range(len(file_list)):
                #file_list[i] = file_list[i][9:15]
                #print(file_list[i])
                ctime = os.path.getctime("./client"+str(q)+"/"+file_list[i])
                hi = str(datetime.fromtimestamp(ctime))
                hms = hi[11:19]
                #ctime = os.path.getctime('./client0/20201031_200941.673-0.png')
                #hi = datetime.datetime.fromtimestamp(ctime)
                #hi = str(datetime.datetime.fromtimestamp(ctime))





                #print(str(hi)[11:19])
                #ctime = os.path.getctime(path or filename)
                if i == 0:
                    #start_time = (int(file_list[i][0:2]) * 3600) + (int(file_list[i][2:4]) * 60) + int(file_list[i][4:6])
                    start_time = (int(hms[0:2]) * 3600) + (int(hms[3:5]) * 60) + int(hms[6:8])
                    flag += 1
                    continue
                if flag == 0:
                    #btime = os.path.getctime(file_list[i-1])
                    btime = os.path.getctime("./client" + str(q) + "/" + file_list[i-1])
                    bhi = str(datetime.fromtimestamp(btime))
                    bhms = bhi[11:19]

                    #start_time = (int(file_list[i - 1][0:2]) * 3600) + (int(file_list[i - 1][2:4]) * 60) + int(file_list[i - 1][4:6])
                    start_time = (int(bhms[0:2]) * 3600) + (int(bhms[3:5]) * 60) + int(bhms[6:8])

                    flag = 1
                    if i != len(file_list) - 1:
                        continue

                #now_time = (int(file_list[i][0:2]) * 3600) + (int(file_list[i][2:4]) * 60) + int(file_list[i][4:6])
                now_time = (int(hms[0:2]) * 3600) + (int(hms[3:5]) * 60) + int(hms[6:8])
                #before_time = (int(file_list[i - 1][0:2]) * 3600) + (int(file_list[i - 1][2:4]) * 60) + int(file_list[i - 1][4:6])
                btime = os.path.getctime("./client" + str(q) + "/" + file_list[i - 1])
                bhi = str(datetime.fromtimestamp(btime))
                bhms = bhi[11:19]

                before_time = (int(bhms[0:2]) * 3600) + (int(bhms[3:5]) * 60) + int(bhms[6:8])

                if i == len(file_list) - 1:
                    print(now_time - start_time)
                    f.write(str(now_time - start_time)+"\n")
                    #print(dir_person[j])

                if flag == 1 and now_time - before_time > 10:  # 시간 분리 기준 == 10초가 넘으면 다른데 갔다왔다고 생각
                    residence_time = before_time - start_time
                    print(residence_time)
                    f.write(str(residence_time)+"\n")
                    flag = 0

        f.close()





# # 원본 코드
# # !/usr/bin/env python3
# # 실행방법 -> terminal -> python face_classifier.py 0 -t 0.35 -d
# from person_db import Person
# from person_db import Face
# from person_db import PersonDB
# import face_recognition
# import numpy as np
# from datetime import datetime
# import cv2
#
#
# class FaceClassifier():
#     def __init__(self, threshold, ratio):
#         self.similarity_threshold = threshold
#         self.ratio = ratio
#
#     def get_face_image(self, frame, box):
#         img_height, img_width = frame.shape[:2]
#         (box_top, box_right, box_bottom, box_left) = box
#         box_width = box_right - box_left
#         box_height = box_bottom - box_top
#         crop_top = max(box_top - box_height, 0)
#         pad_top = -min(box_top - box_height, 0)
#         crop_bottom = min(box_bottom + box_height, img_height - 1)
#         pad_bottom = max(box_bottom + box_height - img_height, 0)
#         crop_left = max(box_left - box_width, 0)
#         pad_left = -min(box_left - box_width, 0)
#         crop_right = min(box_right + box_width, img_width - 1)
#         pad_right = max(box_right + box_width - img_width, 0)
#         face_image = frame[crop_top:crop_bottom, crop_left:crop_right]
#         if (pad_top == 0 and pad_bottom == 0):
#             if (pad_left == 0 and pad_right == 0):
#                 return face_image
#         padded = cv2.copyMakeBorder(face_image, pad_top, pad_bottom,
#                                     pad_left, pad_right, cv2.BORDER_CONSTANT)
#         return padded
#
#     # return list of dlib.rectangle
#     def locate_faces(self, frame):
#         # start_time = time.time()
#         if self.ratio == 1.0:
#             rgb = frame[:, :, ::-1]
#         else:
#             small_frame = cv2.resize(frame, (0, 0), fx=self.ratio, fy=self.ratio)
#             rgb = small_frame[:, :, ::-1]
#         boxes = face_recognition.face_locations(rgb)
#         # elapsed_time = time.time() - start_time
#         # print("locate_faces takes %.3f seconds" % elapsed_time)
#         if self.ratio == 1.0:
#             return boxes
#         boxes_org_size = []
#         for box in boxes:
#             (top, right, bottom, left) = box
#             left = int(left / ratio)
#             right = int(right / ratio)
#             top = int(top / ratio)
#             bottom = int(bottom / ratio)
#             box_org_size = (top, right, bottom, left)
#             boxes_org_size.append(box_org_size)
#         return boxes_org_size
#
#     def detect_faces(self, frame, frame_name):
#         boxes = self.locate_faces(frame)
#         if len(boxes) == 0:
#             return []
#
#         # faces found
#         faces = []
#         now = datetime.now()
#         str_ms = now.strftime('%Y%m%d_%H%M%S.%f')[:-3] + '-'
#         encodings = face_recognition.face_encodings(frame, boxes)
#         for i, box in enumerate(boxes):
#             face_image = self.get_face_image(frame, box)
#             # face = Face(str_ms + str(i) + ".png", face_image, encodings[i])
#             face = Face(frame_name + ".png", face_image, encodings[i])
#             face.location = box
#             faces.append(face)
#         return faces
#
#     def compare_with_known_persons(self, face, persons):
#         if len(persons) == 0:
#             return None
#
#         # see if the face is a match for the faces of known person
#         encodings = [person.encoding for person in persons]
#         distances = face_recognition.face_distance(encodings, face.encoding)
#         index = np.argmin(distances)
#         min_value = distances[index]
#         if min_value < self.similarity_threshold:
#             # face of known person
#             persons[index].add_face(face)
#             # re-calculate encoding
#             persons[index].calculate_average_encoding()
#             face.name = persons[index].name
#             return persons[index]
#
#     def compare_with_unknown_faces(self, face, unknown_faces):
#         if len(unknown_faces) == 0:
#             # this is the first face
#             unknown_faces.append(face)
#             face.name = "unknown"
#             return
#
#         encodings = [face.encoding for face in unknown_faces]
#         distances = face_recognition.face_distance(encodings, face.encoding)
#         index = np.argmin(distances)
#         min_value = distances[index]
#         if min_value < self.similarity_threshold:
#             # two faces are similar - create new person with two faces
#             person = Person()
#             newly_known_face = unknown_faces.pop(index)
#             person.add_face(newly_known_face)
#             person.add_face(face)
#             person.calculate_average_encoding()
#             face.name = person.name
#             newly_known_face.name = person.name
#             return person
#         else:
#             # unknown face
#             unknown_faces.append(face)
#             face.name = "unknown"
#             return None
#
#     def draw_name(self, frame, face):
#         color = (0, 0, 255)
#         thickness = 2
#         (top, right, bottom, left) = face.location
#
#         # draw box
#         width = 20
#         if width > (right - left) // 3:
#             width = (right - left) // 3
#         height = 20
#         if height > (bottom - top) // 3:
#             height = (bottom - top) // 3
#         cv2.line(frame, (left, top), (left + width, top), color, thickness)
#         cv2.line(frame, (right, top), (right - width, top), color, thickness)
#         cv2.line(frame, (left, bottom), (left + width, bottom), color, thickness)
#         cv2.line(frame, (right, bottom), (right - width, bottom), color, thickness)
#         cv2.line(frame, (left, top), (left, top + height), color, thickness)
#         cv2.line(frame, (right, top), (right, top + height), color, thickness)
#         cv2.line(frame, (left, bottom), (left, bottom - height), color, thickness)
#         cv2.line(frame, (right, bottom), (right, bottom - height), color, thickness)
#
#         # draw name
#         # cv2.rectangle(frame, (left, bottom + 35), (right, bottom), (0, 0, 255), cv2.FILLED)
#         font = cv2.FONT_HERSHEY_DUPLEX
#         cv2.putText(frame, face.name, (left + 6, bottom + 30), font, 1.0,
#                     (255, 255, 255), 1)
#
#
# if __name__ == '__main__':
#     import argparse
#     import signal
#     import time
#     import os
#
#     ap = argparse.ArgumentParser()
#     ap.add_argument("inputfile",
#                     help="video file to detect or '0' to detect from web cam")
#     ap.add_argument("-t", "--threshold", default=0.44, type=float,
#                     help="threshold of the similarity (default=0.44)")
#     ap.add_argument("-S", "--seconds", default=1, type=float,
#                     help="seconds between capture")
#     ap.add_argument("-s", "--stop", default=0, type=int,
#                     help="stop detecting after # seconds")
#     ap.add_argument("-k", "--skip", default=0, type=int,
#                     help="skip detecting for # seconds from the start")
#     ap.add_argument("-d", "--display", action='store_true',
#                     help="display the frame in real time")
#     ap.add_argument("-c", "--capture", type=str,
#                     help="save the frames with face in the CAPTURE directory")
#     ap.add_argument("-r", "--resize-ratio", default=1.0, type=float,
#                     help="resize the frame to process (less time, less accuracy)")
#     args = ap.parse_args()
#
#     src_file = args.inputfile
#
#     # 각 라즈베리파이에서 받아온 사진들은 total에 저장되었다고 가정(나중에 파일이름 수정)
#     # ex>
#     # 라즈베리파이1에서 받아온 파일명 -> client1일 경우 밑의 total_img = './client1'로 수정
#     # 라파가 여러개 일 경우 이러한 total_img를 계속 이름을 수정해줘야함
#     # 그리하여 frame_img를 계속 바꾸고 그걸 돌리는 느낌
#     # 즉, 여러개의 라파의 각각의 체류시간을 구하기 위해서는 이 아랫부분을 for 문으로 감싸 라파 갯수만큼 실행시키면 된다.
#     if src_file == "0":
#         total_img = './total'
#         frame_img = os.listdir(total_img)
#         frame_img.sort()
#         src_file = './total/' + frame_img[0]
#
#     src = cv2.VideoCapture(src_file)
#
#     if not src.isOpened():
#         print("cannot open inputfile", src_file)
#         exit(1)
#
#     frame_width = src.get(cv2.CAP_PROP_FRAME_WIDTH)
#     frame_height = src.get(cv2.CAP_PROP_FRAME_HEIGHT)
#     frame_rate = src.get(5)
#     frames_between_capture = int(round(frame_rate * args.seconds))
#
#     print("source", args.inputfile)
#     print("original: %dx%d, %f frame/sec" % (src.get(3), src.get(4), frame_rate))
#     ratio = float(args.resize_ratio)
#     if ratio != 1.0:
#         s = "RESIZE_RATIO: " + args.resize_ratio
#         s += " -> %dx%d" % (int(src.get(3) * ratio), int(src.get(4) * ratio))
#         print(s)
#     print("process every %d frame" % frames_between_capture)
#     print("similarity shreshold:", args.threshold)
#     if args.stop > 0:
#         print("Detecting will be stopped after %d second." % args.stop)
#
#     # load person DB
#     result_dir = "result"
#     pdb = PersonDB()
#     pdb.load_db(result_dir)
#     pdb.print_persons()
#
#     # prepare capture directory
#     num_capture = 0
#     if args.capture:
#         print("Captured frames are saved in '%s' directory." % args.capture)
#         if not os.path.isdir(args.capture):
#             os.mkdir(args.capture)
#
#
#     # set SIGINT (^C) handler
#     def signal_handler(sig, frame):
#         global running
#         running = False
#
#
#     prev_handler = signal.signal(signal.SIGINT, signal_handler)
#     if args.display:
#         print("Press q to stop detecting...")
#     else:
#         print("Press ^C to stop detecting...")
#
#     # fc = FaceClassifier(args.threshold, ratio)
#     fc = FaceClassifier(0.35, 1.0)
#     frame_id = 0
#     running = True
#
#     total_start_time = time.time()
#     frame_cnt = 0
#     while running:
#         if len(frame_img) == frame_cnt:
#             break
#         src_file = './total/' + frame_img[frame_cnt]
#         src = cv2.VideoCapture(src_file)
#
#         ret, frame = src.read()
#         if frame is None:
#             print('hi')
#             break
#
#         frame_id += 1
#         # if frame_id % frames_between_capture != 0:
#         #            continue
#
#         seconds = round(frame_id / frame_rate, 3)
#         if args.stop > 0 and seconds > args.stop:
#             break
#         if seconds < args.skip:
#             continue
#
#         start_time = time.time()
#
#         # this is core
#         # 2020 11 15
#         # faces = fc.detect_faces(frame)
#         faces = fc.detect_faces(frame, frame_img[frame_cnt])
#         frame_cnt += 1
#         for face in faces:
#             person = fc.compare_with_known_persons(face, pdb.persons)
#             if person:
#                 continue
#             person = fc.compare_with_unknown_faces(face, pdb.unknown.faces)
#             if person:
#                 pdb.persons.append(person)
#
#         if args.display or args.capture:
#             for face in faces:
#                 fc.draw_name(frame, face)
#             if args.capture and len(faces) > 0:
#                 now = datetime.now()
#                 filename = now.strftime('%Y%m%d_%H%M%S.%f')[:-3] + '.png'
#                 pathname = os.path.join(args.capture, filename)
#                 # cv2.imwrite(pathname, frame)
#                 cv2.imwrite(frame_img[frame_cnt - 1])
#                 num_capture += 1
#             # if args.display:
#             #     cv2.imshow("Frame", frame)
#             #     # imshow always works with waitKey
#             #     key = cv2.waitKey(1) & 0xFF
#             #     # if the `q` key was pressed, break from the loop
#             #     if key == ord("q"):
#             #         running = False
#
#         elapsed_time = time.time() - start_time
#
#         s = "\rframe " + str(frame_id)
#         s += " @ time %.3f" % seconds
#         s += " takes %.3f second" % elapsed_time
#         s += ", %d new faces" % len(faces)
#         s += " -> " + repr(pdb)
#         if num_capture > 0:
#             s += ", %d captures" % num_capture
#         print(s, end="    ")
#
#     # restore SIGINT (^C) handler
#     signal.signal(signal.SIGINT, prev_handler)
#     running = False
#     src.release()
#     total_elapsed_time = time.time() - total_start_time
#     print()
#     print("total elapsed time: %.3f second" % total_elapsed_time)
#
#     pdb.save_db(result_dir)
#     pdb.print_persons()
#
#     # 체류시간 계산하기
#     path_person_dir = './result/'
#
#     temp = os.listdir(path_person_dir)
#     dir_person = []
#
#     # person 디렉터리 이름 가져오기 -> dir_person에 저장
#     for i in range(len(temp)):
#         if temp[i].startswith('person_'):
#             dir_person.append(temp[i])
#     # print(dir_person)
#
#     #
#
#     for j in range(len(dir_person)):
#         # path_dir = './result/person_01'
#         path_dir = './result/' + dir_person[j]
#         file_list = os.listdir(path_dir)
#
#         file_list.sort()
#
#         flag = 0
#         start_time = 0
#         now_time = 0
#         for i in range(len(file_list)):
#             file_list[i] = file_list[i][9:15]
#             if i == 0:
#                 start_time = (int(file_list[i][0:2]) * 3600) + (int(file_list[i][2:4]) * 60) + int(file_list[i][4:6])
#                 flag += 1
#                 continue
#             if flag == 0:
#                 start_time = (int(file_list[i - 1][0:2]) * 3600) + (int(file_list[i - 1][2:4]) * 60) + int(
#                     file_list[i - 1][4:6])
#                 flag = 1
#                 if i != len(file_list) - 1:
#                     continue
#
#             now_time = (int(file_list[i][0:2]) * 3600) + (int(file_list[i][2:4]) * 60) + int(file_list[i][4:6])
#             before_time = (int(file_list[i - 1][0:2]) * 3600) + (int(file_list[i - 1][2:4]) * 60) + int(
#                 file_list[i - 1][4:6])
#
#             if i == len(file_list) - 1:
#                 print(now_time - start_time)
#                 print(dir_person[j])
#
#             if flag == 1 and now_time - before_time > 10:  # 시간 분리 기준
#                 residence_time = before_time - start_time
#                 print(residence_time)
#                 flag = 0
