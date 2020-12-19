import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import os
import matplotlib.pyplot as plt

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
agemodel = tensorflow.keras.models.load_model('age.h5')
gendermodel = tensorflow.keras.models.load_model('gender.h5')

# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1.
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# Replace this with the path to your image
path = './testset100/'
temp = os.listdir(path)
dir_person = []
#real_sex = {'man':50,'woman':50}
real_sex = [50,50]
real_age = [0,20,20,20,20,20,0]
sex = {'man':0,'woman':0}
age = [0,0,0,0,0,0,0]   #{'0~9':0,'10~19':0,'20~29':0,'30~39':0,'40~49':0,'50~59':0,'60up':0}

for i in range(len(temp)):
    dir_person.append(temp[i])
print(temp)

for i in range(len(temp)):
    image = Image.open(path+dir_person[i])
    #resize the image to a 224x224 with the same strategy as in TM2:
    #resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    #turn the image into a numpy array
    image_array = np.asarray(image)

    # display the resized image
    #image.show()

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    age_prediction = agemodel.predict(data)
    gender_prediction = gendermodel.predict(data)

    print("Age")
    print(age_prediction)
    print("Gender")
    print(gender_prediction)
    #print(gender_prediction[0][0])

    max = 0
    max_index = -1
    for i in range(7):
        if max < age_prediction[0][i]:
            max = age_prediction[0][i]
            max_index = i
    age[max_index]+=1
    if gender_prediction[0][0] > gender_prediction[0][1]:
        sex['man']+=1
    else:
        sex['woman']+=1

print('실제 결과 값')
print(real_age)
print(real_sex)

print('예측 결과 값')
print(age)
print(sex)

sexlist=[]
sexlist.append(sex['man'])
sexlist.append(sex['woman'])
#visualize
#실제 나이
x = np.arange(7)
years = ['0-9', '10-19', '20-29','30-39','40-49','50-59','60up']
plt.bar(x, real_age)
plt.xticks(x, years)
for i, v in enumerate(x):
    plt.text(v, real_age[i], real_age[i],                 # 좌표 (x축 = v, y축 = y[0]..y[1], 표시 = y[0]..y[1])
             fontsize = 9,
             color='blue',
             horizontalalignment='center',  # horizontalalignment (left, center, right)
             verticalalignment='bottom')    # verticalalignment (top, center, bottom)
plt.show()
#실제 성별
y = np.arange(2)
standard_sex = ['Male', 'Female']
plt.bar(y, real_sex)
plt.xticks(y,standard_sex)
for i, v in enumerate(y):
    plt.text(v, real_sex[i], real_sex[i],                 # 좌표 (x축 = v, y축 = y[0]..y[1], 표시 = y[0]..y[1])
             fontsize = 9,
             color='blue',
             horizontalalignment='center',  # horizontalalignment (left, center, right)
             verticalalignment='bottom')    # verticalalignment (top, center, bottom)
plt.show()
#예측 나이
x = np.arange(7)
years = ['0-9', '10-19', '20-29','30-39','40-49','50-59','60up']
print(age)
plt.bar(x, age)
plt.xticks(x, years)
for i, v in enumerate(x):
    plt.text(v, age[i], age[i],                 # 좌표 (x축 = v, y축 = y[0]..y[1], 표시 = y[0]..y[1])
             fontsize = 9,
             color='blue',
             horizontalalignment='center',  # horizontalalignment (left, center, right)
             verticalalignment='bottom')    # verticalalignment (top, center, bottom)
plt.show()

#예측 성별
y = np.arange(2)
standard_sex = ['Male', 'Female']
plt.bar(y, sexlist)
plt.xticks(y,standard_sex)
for i, v in enumerate(y):
    plt.text(v, sexlist[i], sexlist[i],                 # 좌표 (x축 = v, y축 = y[0]..y[1], 표시 = y[0]..y[1])
             fontsize = 9,
             color='blue',
             horizontalalignment='center',  # horizontalalignment (left, center, right)
             verticalalignment='bottom')    # verticalalignment (top, center, bottom)
plt.show()