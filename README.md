# ECCE-Thesis-Files
2019-2020 ECCE Undergraduate Thesis

Title: NAO Physical Connect Four Game Interaction with Use of Image Processing, 
Machine Learning for Game Logic, and Inverse Kinematics for Movement.

## Main Program Flow

Starting from Main, clients are first established for communicating with the NAO robot of class ALProxy.
Each ALProxy is used to access an API, declared as the first parameter upon instantiation.

The first clients utilized are of ALAutonomousLife and ALRobotPosture APIs. These are used in conjunction
to set NAO in a steady/motionless crouching state. The next client utilized is of the ALMemory API, which
is used to subscribe to events of a given name, through a class extending ALModule with a callback method.
This is used to first subscribe to the event "PictureDetected", which results in an invoked callback upon
detection of a learned image. After this, a client of the ALSpeechRecognition API is repeatedly called
to set words for detection using the ALMemory subscription. The speech recognition is used to keep a flow
while setting the game AI parameters of difficulty and startpiece.

In between the various subscriptions for waiting for the recognition of input video or speech, an instance
of the ALTexttoSpeechProxy is made to output phrases to guide the user to what NAO is doing or what the
user needs to do at the given moment.

Once the initial parameters are set, NAO can then begin a loop for taking in the input image of the current
game state, and outputting its move through pointing. 

For taking in the input image, another client is used to retrieve the camera feed of NAO's top camera. This
image is then processed through the use of opencv. An initial circle detection is performed using Hough
Circle Transform. This is used to draw all detected circles within the image as filled black on white
background. The board is then found on the drawn black and white image using the opencv function 
detectCircleGrid, which expects a clean black and white input image with clearly defined circles, looking 
for the right grid size of (6 rows, 7 columns). The image is then converted to HSV for reading the colors
and the coordinates for the centers of the circles within the detected grid. Upon reading the color,
the board is then retrieved in array format for the game state to be passed to the game handling logic.

The game logic is handled by a player object with an attached neural network model selected through the
difficulty setting. The player is made to return the coordinates of the move that the neural network
determines as the best for the given game state.

The output move is then effected through the Cartesian Control API of NAO, which is part of the NAOqi
framework. Consideration was made to use the forward and inverse kinematics implementations for NAO v5 
found at https://github.com/kouretes/NAOKinematics.git, however, it was opted out of due to a lack of
usage guidance, as well as the presence of comments that mark the code as under construction for the
given NAO distribution that is needed. Math is done through measured knowns, as well as assumptions and
retrieved coordinates from forward kinematics to determine the coordinates for placement of the end
effectors of NAO in its arms. The performance of the motion to the determined coordinates is done through
the built in IK solver within the Cartesian Control API.

## Credits

The NAOqi API and NAO itself comes from Aldebaran. The main documentation for the utilized version for
NAOqi has documentation available at http://doc.aldebaran.com/2-1/index.html.

The cv2 distribution of OpenCV and pillow distribution of PIL were used for handling images.

DRL adopted from a fork of https://github.com/AppliedDataSciencePartners/DeepReinforcementLearning.git
with significant edits to get working on Win 10 Python 2.7.16 32bit with an unofficial distribution
of Tensorflow (Tensorflow on Windows is normally only for Python 3.5-3.7 64bit).

This was done in order to retain the ability to use NAOqi, which is the framework for handling the NAO
robot. NAOqi in its 2.1.4.13 Windows distribution is only available on Python 2.7 32bit. 

## Training

Training was initially performed on the unofficial distribution with Python 2.7.16,
however, a major problem was encountered with the memory size required for the training process,
as well as the pickling process (for being able to save the memory object to resume at checkpoints). 

Given that problem, it was then decided that training would be conducted on a 64bit release of Python.
It was decided that the distribution to be used would be the latest python 3.7 release, since tensorflow
had yet to be distributed for python 3.8. This also allowed for official support in the gpu distribution
of tensorflow. 

This dealt with the both issues, since the gpu distribution of tensorflow allows for much easier
learning, while the 64bit release allows for much larger pickle outputs and inputs for object storage
and retrieval.

The generated models through training on Python 3 can be ported back onto the Python 2 version of the
Learning for compatibility with the Windows NAOqi distribution.