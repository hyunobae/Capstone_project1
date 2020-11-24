import matplotlib.pyplot as plt
import numpy as np
import os

path_person_dir = './textfile/'

temp = os.listdir(path_person_dir)
dir_person = []
values = [0,0,0,0,0,0,0,0,0,0] #age 저장리스트
val = [0,0]    #성별 저장리스트 index0 : male, index1 : female


# person 디렉터리 이름 가져오기 -> dir_person에 저장
for i in range(len(temp)):
    if temp[i].startswith('person'):
        dir_person.append(temp[i])
sex = {'Male' : 0,'Female' : 0}

def f1(x):
    return sex[x]

for i in range(len(dir_person)):
    f = open(path_person_dir + dir_person[i],'r')
    test = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    age = []
    print(dir_person[i])
    while True:
        line = f.readline()
        if not line:
            break
        person = line.split(" ")
        if len(person) < 3:
            continue
        elif len(person) >=5:
            person = person[1:]
        #print(person[2])
        sex[person[2]]+=1
        age.append(int(person[3]))

    key_max = max(sex.keys(),key=f1)    #Male or Female
    if(key_max == 'Male'):
        val[0]+=1
    else:
        val[1]+=1

    #
    for i in range(len(age)):
        test[int(age[i]/10)] += 1
    print(test)

    max_age=0
    max_index=0
    for i in range(len(test)):
        if max_age < test[i]:
            max_index = i
            max_age = test[i]

    test.clear()
    #
    avg_age = round(sum(age,0.0)/len(age))  #평균 나이

    #values[int(avg_age/10)]+=1
    values[max_index] += 1

#print(values)
#print(val)
x = np.arange(10)
years = ['0-9', '10-19', '20-29','30-39','40-49','50-59','60-69','70-79','80-89','90-99']
#values = [3,12,3,4,0,0,0,0,0,0]

plt.bar(x, values)
plt.xticks(x, years)
plt.show()


y = np.arange(2)
sex = ['Male', 'Female']
#val = [14,22]

plt.bar(y, val)
plt.xticks(y,sex)
plt.show()