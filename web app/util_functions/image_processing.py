import cv2
import numpy as np



def draw_map_on_image(image, map):
    x = image.shape[0]
    y = image.shape[1]
    
    for i in range(x):
        for j in range(y):
            if map[i][j] == 0:
                continue
            image[i][j] = np.array([0,0,255],dtype='uint8')
    return image