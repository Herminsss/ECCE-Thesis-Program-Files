import sys
import numpy as np
from naoqi import ALProxy
import motion

import config

def pointAtCircle(circles, move):

    motionProxy = ALProxy("ALMotion", config.NAO_IP, config.NAO_PORT)

    board_height_res = circles[5][0][1] - circles[0][0][1]
    board_width_res = circles[0][6][0] - circles[0][0][0]

    print (board_height_res, type(board_height_res), board_width_res, type(board_width_res))

    # Originally, "*(0.5)" was "*(1/2)", but python considers the data types of numbers dynamically, so 1 and 2 get assigned as ints
    # and then operated first since the term is in parentheses, leading to an int division bearing an answer of 0, making 
    # "*(1/2)" equivalent to "*(0)"
    x = (   0.142/(2*np.tan(np.radians((board_width_res/config.CAMERA_HRES)*(config.CAMERA_HDEG)*(0.5))))
            + 0.105/(2*np.tan(np.radians((board_height_res/config.CAMERA_VRES)*(config.CAMERA_VDEG)*(0.5)))) ) / 2

    # y = x * np.tan( np.radians(abs(circles[move[0]][move[1]][1]-config.CAMERA_HRES/2) * (config.CAMERA_HDEG)) )
    # y = y if circles[move[0]][move[1]] < config.CAMERA_HRES/2 else -y

    y = (config.CAMERA_HRES/2 - circles[move[0]][move[1]][1]) / board_width_res * 0.142

    # z = x * np.tan( np.radians(abs(circles[move[0]][move[1]][0]-config.CAMERA_VRES) * (config.CAMERA_VDEG)) )
    # z = z if circles[move[0]][move[1]] < config.CAMERA_VRES else -z

    z = (config.CAMERA_VRES/2 - circles[move[0]][move[1]][0]) / board_height_res * 0.105

    # Example showing how to use positionInterpolations
    space           = motion.FRAME_ROBOT
    useSensorValues = True
    isAbsolute      = True

    camera_position = motionProxy.getPosition("CameraTop", space, useSensorValues)
    left_shoulder_position = motionProxy.getPosition("LShoulder", space, useSensorValues)
    right_shoulder_position = motionProxy.getPosition("RShoulder", space, useSensorValues)

    print(camera_position)
    x += camera_position[0]
    y += camera_position[1]
    z += camera_position[2]
    print(x, y, z)

    x_right_arm = 0
    y_right_arm = 0
    z_right_arm = 0

    x_left_arm = 0
    y_left_arm = 0
    z_left_arm = 0

    if y >= -0.01:
        x_left_arm = x - left_shoulder_position[0]
        y_left_arm = y - left_shoulder_position[1]
        z_left_arm = z - left_shoulder_position[2]

        left_ratio = config.ARM_LENGTH/np.sqrt(x_left_arm**2 + y_left_arm**2 + z_left_arm**2)
        x_left_arm = x_left_arm * left_ratio
        y_left_arm = y_left_arm * left_ratio
        z_left_arm = z_left_arm * left_ratio

        x_left_arm += left_shoulder_position[0]
        y_left_arm += left_shoulder_position[1]
        z_left_arm += left_shoulder_position[2]

    if y <= 0.01:
        x_right_arm = x - right_shoulder_position[0]
        y_right_arm = y - right_shoulder_position[1]
        z_right_arm = z - right_shoulder_position[2]

        right_ratio = config.ARM_LENGTH/np.sqrt(x_right_arm**2 + y_right_arm**2 + z_right_arm**2)
        x_right_arm = x_right_arm * right_ratio
        y_right_arm = y_right_arm * right_ratio
        z_right_arm = z_right_arm * right_ratio

        x_right_arm += right_shoulder_position[0]
        y_right_arm += right_shoulder_position[1]
        z_right_arm += right_shoulder_position[2]

    print(x_left_arm, y_left_arm, z_left_arm)
    print(x_right_arm, y_right_arm, z_right_arm)

    # Motion of Arms with block process
    effectorList = ["LArm", "RArm"]
    axisMaskList = [motion.AXIS_MASK_VEL, motion.AXIS_MASK_VEL]
    timeList     = [[2.0], [2.0]]         # seconds
    pathList     = [[[x_left_arm, y_left_arm, z_left_arm, 0.0, 0.0, 0.0]],
                    [[x_right_arm, y_right_arm, z_right_arm, 0.0, 0.0, 0.0]]]
    motionProxy.positionInterpolations(effectorList, space, pathList,
                                 axisMaskList, timeList, isAbsolute)
 
    speechProxy = ALProxy("ALTextToSpeech", config.NAO_IP, config.NAO_PORT)
    speechProxy.say("I shall place my move at column" + str(move[1]+1) + "\n\n from the left")

# def restArms():
    
#     motionProxy = ALProxy("ALMotion", config.NAO_IP, config.NAO_PORT)
#     space           = motion.FRAME_ROBOT
#     isAbsolute      = False
#     effectorList = ["LArm", "RArm"]
#     axisMaskList = [motion.AXIS_MASK_VEL, motion.AXIS_MASK_VEL]
#     timeList     = [[2.0], [2.0]]         # seconds
#     pathList     = [[[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
#                     [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]]
#     motionProxy.positionInterpolations(effectorList, space, pathList,
#                                  axisMaskList, timeList, isAbsolute)