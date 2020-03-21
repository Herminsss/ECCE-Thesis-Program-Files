import cv2
import numpy as np
import config

# --------------

def __drawCircles(img, grayscale_img):
    cimg = cv2.medianBlur(grayscale_img, 5)

    circles = cv2.HoughCircles(cimg, cv2.HOUGH_GRADIENT, 1, 10,
                                param1=80, param2=20, minRadius=5, maxRadius=20)

    circles = np.uint16(np.around(circles))
    for i in circles[0]:
        # draw the outer circle
        cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle
        cv2.circle(img,(i[0],i[1]),2,(255,0,0),3)

    cv2.imwrite(config.IMAGE_PATH + 'detectedCircles.png', img)

    # draw the detected circles as filled black on a white background
    cimg.fill(255)
    for i in circles[0]:
        cv2.circle(cimg, (i[0], i[1]), i[2], (0, 0, 0), thickness=-1)

    cv2.imwrite(config.IMAGE_PATH + 'circles.png', cimg)
    return cimg

def __detectCircleGrid(img, cimg):
    gridexists = cv2.findCirclesGrid(cimg, (7, 6))

    circles = [[[None for c in range(2)] for x in range(7)] for y in range(6)]
    index = 0

    try:
        for i in gridexists[1]:
            circles[int(index / 7)][index % 7] = (i[0][0], i[0][1])
            index += 1

        for y in range(6):
            for x in range(7):
                # draw the outer circle
                cv2.circle(img, circles[y][x], 2, (0,255,255), 3)

    except:
        pass

    cv2.imwrite(config.IMAGE_PATH + 'detectedCircleGrid.png', img)
    
    return circles

def __colorDetection(img, circles):
    HSV_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cv2.imwrite(config.IMAGE_PATH + 'HSV_Img.png', HSV_img)

    # low_red = np.array([161, 155, 84])
    # high_red = np.array([179, 255, 255])

    # low_yellow = np.array([20, 100, 100])
    # high_yellow = np.array([30, 255, 255])
    
    low_red = np.array([50, 100, 84])
    high_red = np.array([179, 255, 255])

    low_yellow = np.array([0, 100, 100])
    high_yellow = np.array([50, 255, 255])

    board = [[0 for x in range(7)] for y in range(6)]

    colors = np.zeros((6,7,3), dtype=int)
    
    try:
        for row in range(6):
            for column in range(7):
                x_coor = int(circles[row][column][0]-4)
                y_coor = int(circles[row][column][1]-4)
                color = np.array([0, 0, 0])
                color = color.astype(int)
                i = 0
                for sample_y in range (9):
                    for sample_x in range (9):
                        color = np.add(color, HSV_img[y_coor + sample_y, x_coor + sample_x])

                color /= 81
                
                colors[6][7] = color

                if board[row-1][column] == 0:
                    if (np.subtract(color, low_red) > 0).all() and (np.subtract(color, high_red) < 0).all():
                        board[row][column] = 1
                    if (np.subtract(color, low_yellow) > 0).all() and (np.subtract(color, high_yellow) < 0).all():
                        board[row][column] = -1

                #if an above coordinate has already been detected to have a piece, force piece detection (cannot be empty space)
                #by setting any hue value above 100 as red and any hue value below 100 as yellow
                #this is done to prevent illegal board states from being read 
                else:
                    if(color[0] >= high_yellow[0]):
                        board[row][column] = 1
                    else:
                        board[row][column] = -1

        for row in colors:
            print(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

        return board

    #if the number of circles is less than required, output that the gameboard detection failed
    except:
        print "failed to detect game board"
        return None

# --------------

def retrieveGameBoard(img_name):
    img = cv2.imread(config.IMAGE_PATH + img_name)
    img_copy = cv2.imread(config.IMAGE_PATH + img_name)
    grayscale_img = cv2.imread(config.IMAGE_PATH + img_name, 0)

    cimg = __drawCircles(img, grayscale_img)
    circles = __detectCircleGrid(img, cimg)
    gameboard = __colorDetection(img_copy, circles)
    return circles, gameboard