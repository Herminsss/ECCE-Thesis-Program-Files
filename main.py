import os
import sys
import time
import naoqi
from naoqi import ALProxy
from naoqi import ALModule
from naoqi import ALBroker

import config
from DRL import setPlayer
from DRL import makeMove
from move import processGameBoard
# from NAOmotion import restArms

class eventModule(ALModule):
  """python class myModule test auto documentation"""

  def dataDetected(self, strVarName, value, strMessage):
    """callback when data is detected"""

    print("Data Detected", strVarName, value, strMessage)
    global dataDetected
    dataDetected = value[0]

## Define Proxies for use of NAO's modules
behaviorProxy = ALProxy("ALBehaviorManager", config.NAO_IP, config.NAO_PORT)
behaviorProxy.stopAllBehaviors()

autoLifeProxy = ALProxy("ALAutonomousLife", config.NAO_IP, config.NAO_PORT)

postureProxy = ALProxy("ALRobotPosture", config.NAO_IP, config.NAO_PORT)

broker = ALBroker("pythonBroker", config.PC_IP, config.PC_PORT, config.NAO_IP, config.NAO_PORT)
module_name = "event_catcher"
event_catcher = eventModule(module_name)
subscriberProxy = ALProxy("ALMemory", config.NAO_IP, config.NAO_PORT)

speechProxy = ALProxy("ALTextToSpeech", config.NAO_IP, config.NAO_PORT)

speechRecogProxy = ALProxy("ALSpeechRecognition", config.NAO_IP, config.NAO_PORT)
speechRecogProxy.setLanguage("English")

## Start Program

# stay motionless unless given an exact movement while crouching for the duration of the program
# possible states are "solitary", "interactive", "disabled", "safeguard"
autoLifeProxy.setState("disabled")
postureProxy.goToPosture("Crouch", 0.5)

# proceed with program if connect 4 board is detected
dataDetected = None
event_name = "PictureDetected"
subscriberProxy.subscribeToEvent(event_name, module_name, "dataDetected")

while dataDetected == None:
  time.sleep(2)
  print(dataDetected)

subscriberProxy.unsubscribeToEvent(event_name, module_name)

# say connect 4 board has been detected
speechProxy.say("""Connect 4 Board Detected.

                  Please select the difficulty:
                  Easy,
                  Medium,
                  or Hard""")

speechRecogProxy.pause(True)
vocabulary = ["Easy", "Medium", "Hard"]
speechRecogProxy.setVocabulary(vocabulary, False)
speechRecogProxy.pause(False)

dataDetected = None
event_name = "WordRecognized"
subscriberProxy.subscribeToEvent(event_name, module_name, "dataDetected")

while dataDetected == None:
  time.sleep(2)
  print(dataDetected)

subscriberProxy.unsubscribeToEvent(event_name, module_name)

difficulty = dataDetected

speechProxy.say("You selected: " + difficulty + """.

                Please give me a moment to set the difficulty""")

player = setPlayer(config.SELECT_DIFFICULTY[difficulty])

speechProxy.say("""Done setting the difficulty.

                  Red goes first.
                  Yellow goes second.

                  Which color would you like to play?""")

speechRecogProxy.pause(True)
vocabulary = ["Red", "Yellow"]
speechRecogProxy.setVocabulary(vocabulary, False)
speechRecogProxy.pause(False)

dataDetected = None
event_name = "WordRecognized"
subscriberProxy.subscribeToEvent(event_name, module_name, "dataDetected")

while dataDetected == None:
  time.sleep(2)
  print(dataDetected)

subscriberProxy.unsubscribeToEvent(event_name, module_name)

piece = dataDetected

if piece == "Red":
  speechProxy.say("""Alright!
                    
                    I'll play second.

                    Tell me when it's my turn, and then I'll point my move""")
  NAOpiece = -1

  speechRecogProxy.pause(True)
  vocabulary = ["turn", "you", "your"]
  speechRecogProxy.setVocabulary(vocabulary, True)
  speechRecogProxy.pause(False)

  dataDetected = None
  event_name = "WordRecognized"
  subscriberProxy.subscribeToEvent(event_name, module_name, "dataDetected")

  while dataDetected == None:
    time.sleep(2)
    print(dataDetected)

  subscriberProxy.unsubscribeToEvent(event_name, module_name)

elif piece == "Yellow":
  speechProxy.say("""Alright!
                    
                    I'll play first.
                    
                    I'll point my move, and I need you to perform it for me""")
  NAOpiece = 1

while 1:
  result = processGameBoard(player, NAOpiece)

  if result == 0:
    speechProxy.say("""Here is my move.

                        Please tell me when it is my turn again.""")

    speechRecogProxy.pause(True)
    vocabulary = ["turn", "you", "your"]
    speechRecogProxy.setVocabulary(vocabulary, True)
    speechRecogProxy.pause(False)

    dataDetected = None
    event_name = "WordRecognized"
    subscriberProxy.subscribeToEvent(event_name, module_name, "dataDetected")

    while dataDetected == None:
      time.sleep(2)
      print(dataDetected)

    subscriberProxy.unsubscribeToEvent(event_name, module_name)

    postureProxy.goToPosture("Crouch", 0.5)

  elif result == 1:
    speechProxy.say("""Please readjust the board or lighting.

                      I was unable to detect it correctly.

                      I shall retry in five seconds.""")
    time.sleep(5)

  else:
    if result == 2:
      speechProxy.say("""The game has ended in a draw.
                        
                          I'll beat you next time!""")

    elif result == 3:
      speechProxy.say("""I won.
      
                          I must be at the top of my game.""")
      if difficulty != "Easy":
        speechProxy.say("""Try selecting a lower difficulty next time.""")

    elif result == 4:
      speechProxy.say("""I lost.
      
                          You played really well!""")
      if difficulty != "Hard":
        speechProxy.say("""Try selecting a higher difficulty next time.""")

    time.sleep(3)
    postureProxy.goToPosture("Crouch", 0.5)
    speechProxy.say("""Alright, thanks for playing with me!""")
    break
