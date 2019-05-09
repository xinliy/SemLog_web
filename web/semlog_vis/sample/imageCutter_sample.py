import sys
sys.path.append("..")

from web.semlog_vis import cut_object
import matplotlib.pyplot as plt


img = cut_object('rgb_object.png', 'mask_object.png', (175, 0, 170))

plt.imshow(img)
plt.show()
