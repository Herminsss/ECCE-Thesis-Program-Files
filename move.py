from NAOcapture import retrieveNaoImage
from circle import retrieveGameBoard
from DRL import makeMove
from NAOmotion import pointAtCircle
from ConnectFour import winner

#returns 0 if game resumes as normal, 1 if there was an error detecting the board
#2 if the game ended in a draw, 3 if NAO won, 4 if the human won
def processGameBoard(player, NAOpiece):

  img_name = "capturedImg.png"
  retrieveNaoImage(img_name)
  circles, gameboard = retrieveGameBoard(img_name)
  if gameboard == None:
    return 1

  for i in gameboard:
    print(i)

  if winner(gameboard) == 0:
    if all(piece != 0 for piece in gameboard[0]):
      return 2
    else:
      pass
    
  elif winner(gameboard) == NAOpiece:
    return 3
    print ("NAO won early")

  else:
    return 4

  move = makeMove(gameboard, NAOpiece, player)

  print(move)

  pointAtCircle(circles, move)

  gameboard[move[0]][move[1]] = NAOpiece

  if winner(gameboard) == 0:
    if all(piece != 0 for piece in gameboard[0]):
      return 2
    else:
      return 0
  
  elif winner(gameboard) == NAOpiece:
    return 3

  else:
    return 4


