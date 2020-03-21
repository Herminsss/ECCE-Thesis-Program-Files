import sys
import numpy as np
from naoqi import ALProxy
import motion
import config

#coordinates from top camera
x, y, z = (0.3766319919462242, -0.022821428571428572, 0.02)

motionProxy = ALProxy("ALMotion", config.NAO_IP, config.NAO_PORT)

autoLifeProxy = ALProxy("ALAutonomousLife", config.NAO_IP, config.NAO_PORT)

postureProxy = ALProxy("ALRobotPosture", config.NAO_IP, config.NAO_PORT)

autoLifeProxy.setState("disabled")
postureProxy.goToPosture("Crouch", 0.5)

# Example showing how to use positionInterpolations
space           = motion.FRAME_ROBOT
useSensorValues = True
isAbsolute      = True

camera_position = motionProxy.getPosition("CameraTop", space, useSensorValues)
left_shoulder_position = motionProxy.getPosition("LShoulder", space, useSensorValues)
right_shoulder_position = motionProxy.getPosition("RShoulder", space, useSensorValues)

print(camera_position)
print(left_shoulder_position)
print(right_shoulder_position)
x += camera_position[0]
y += camera_position[1]
z += camera_position[2]

x_left_arm = x - left_shoulder_position[0]
y_left_arm = y - left_shoulder_position[1]
z_left_arm = z - left_shoulder_position[2]

x_right_arm = x - right_shoulder_position[0]
y_right_arm = y - right_shoulder_position[1]
z_right_arm = z - right_shoulder_position[2]

left_ratio = config.ARM_LENGTH/np.sqrt(x_left_arm**2 + y_left_arm**2 + z_left_arm**2)
x_left_arm = x_left_arm * left_ratio
y_left_arm = y_left_arm * left_ratio
z_left_arm = z_left_arm * left_ratio

right_ratio = config.ARM_LENGTH/np.sqrt(x_right_arm**2 + y_right_arm**2 + z_right_arm**2)
x_right_arm = x_right_arm * right_ratio
y_right_arm = y_right_arm * right_ratio
z_right_arm = z_right_arm * right_ratio

x_left_arm += left_shoulder_position[0]
y_left_arm += left_shoulder_position[1]
z_left_arm += left_shoulder_position[2]

x_right_arm += right_shoulder_position[0]
y_right_arm += right_shoulder_position[1]
z_right_arm += right_shoulder_position[2]

print(x, y, z)
print(x_left_arm, y_left_arm, z_left_arm)
print(x_right_arm, y_right_arm, z_right_arm)

# Motion of Arms with block process
effectorList = ["LArm", "RArm"]
axisMaskList = [motion.AXIS_MASK_VEL, motion.AXIS_MASK_VEL]
timeList     = [[2.5], [2.5]]         # seconds
pathList     = [[[x_left_arm, y_left_arm, z_left_arm, 0.0, 0.0, 0.0]],
                [[x_right_arm, y_right_arm, z_right_arm, 0.0, 0.0, 0.0]]]
motionProxy.positionInterpolations(effectorList, space, pathList,
                              axisMaskList, timeList, isAbsolute)