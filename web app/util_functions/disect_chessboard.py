import cv2


def get_disected_grid(image):
    """
    Image : will be getten
    -----
    Return : grayscale  image,  Grid 8 x 8

    """

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    edges_thresh_image = cv2.Canny(gray_image, 100, 200, None, 3, False)

    side_l = edges_thresh_image.shape[0] // 8

    vertical_file = ['8','7','6','5','4','3','2','1']
    horizontal_file = ['a','b','c','d','e','f','g','h']

    grid = {}
    for i in range(8):
        for j in range(8):
            grid[horizontal_file[j]+vertical_file[i]] = {'x1':side_l * i, 'y1': side_l * j,'x2':side_l*(i+1),'y2':side_l*(j+1)}

    return edges_thresh_image, grid, gray_image



if __name__ == '__main__':
    img = cv2.imread(f'warped_chessboard0.jpg')
    print(get_disected_grid(img))