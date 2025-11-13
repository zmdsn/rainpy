import os
print(os.getenv("UV_PUBLISH_TOKEN"))

# %%
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
x = [1, 2, 3, 4, 5]   # x轴数据
y = [4, 7, 2, 9, 5]   # y轴数据

plt.plot(x, y)
plt.show()





# %%
import rainpy as rp
dir(rp)