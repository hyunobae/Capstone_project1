import os.path, time

path_person_dir = './result/'

temp = os.listdir(path_person_dir)
dir_person = []

# person 디렉터리 이름 가져오기 -> dir_person에 저장
for i in range(len(temp)):
    if temp[i].startswith('person_'):
        dir_person.append(temp[i])
#print(dir_person)

#

for j in range(len(dir_person)):
    #path_dir = './result/person_01'
    path_dir = './result/'+dir_person[j]
    file_list = os.listdir(path_dir)


    file_list.sort()

    flag = 0
    start_time = 0
    now_time = 0
    for i in range(len(file_list)):
        file_list[i] = file_list[i][9:15]
        if i==0:
            start_time = (int(file_list[i][0:2]) * 3600) + (int(file_list[i][2:4]) * 60) + int(file_list[i][4:6])
            flag+=1
            continue
        if flag == 0:
            start_time = (int(file_list[i-1][0:2]) * 3600) + (int(file_list[i-1][2:4]) * 60) + int(file_list[i-1][4:6])
            flag = 1
            if i!=len(file_list)-1:
                continue

        now_time = (int(file_list[i][0:2]) * 3600) + (int(file_list[i][2:4]) * 60) + int(file_list[i][4:6])
        before_time = (int(file_list[i-1][0:2]) * 3600) + (int(file_list[i-1][2:4]) * 60) + int(file_list[i-1][4:6])

        if i == len(file_list)-1:
            print(now_time-start_time)
            print(dir_person[j])

        if flag==1 and now_time - before_time > 10: #시간 분리 기준
            residence_time = before_time - start_time
            print(residence_time)
            flag = 0
