import matplotlib.pyplot as plt
import numpy as np

x = np.arange(10)#연령 별 방문자 수
years = ['0-9', '10-19', '20-29','30-39','40-49','50-59','60-69','70-79','80-89','90-99']
values = [3,12,3,4,0,0,0,0,0,0]

plt.bar(x, values)
plt.xticks(x, years)
plt.show()


# y = np.arange(2)#방문자 성
# sex = ['Male', 'Female']
# val = [14,22]
#
# plt.bar(y, val)
# plt.xticks(y,sex)
# plt.show()