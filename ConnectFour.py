def winner(board):
  #row check
  for y in range(6):
    last = 0
    count = 0
    for x in range(7):
      if board[y][x] == 0:
        last = 0
        count = 0
      elif board[y][x] == -1:
        if last != -1:
          count = 0
        last = -1
        count += 1
      elif board[y][x] == 1:
        if last != 1:
          count = 0
        last = 1
        count += 1
      if count == 4:
        return last
      
  #column check
  for x in range(7):
    last = 0
    count = 0
    for y in range(6):
      if board[y][x] == 0:
        break
      elif board[y][x] == -1:
        if last != -1:
          count = 0
        last = -1
        count+=1
      elif board[y][x] == 1:
        if last != 1:
          count = 0
        last = 1
        count+=1
      if count == 4:
        return last
      
  #diagonal check
  #/
  for n in range(-2, 4):
    last = 0
    count = 0
    for y in range(6):
      if (y+n < 7) and (y+n > -1):
        #print(y+n,y) #used to check the diagonals that are passed through
        if board[y][y+n] == 0:
          last = 0
          count = 0
        elif board[y][y+n] == -1:
          if last != -1:
            count = 0
          last = -1
          count+=1
        elif board[y][y+n] == 1:
          if last != 1:
            count = 0
          last = 1
          count+=1
        if count == 4:
          return last
      
  #\
  for n in range(3, 9):
    last = 0
    count = 0
    for y in range (6):
      if (n-y < 7) and (n-y > 2):
        #print(n-y,y) #used to check the diagonals that are passed through
        if board[y][n-y] == 0:
          last = 0
          count = 0
        elif board[y][n-y] == -1:
          if last != -1:
            count = 0
          last = -1
          count+=1
        elif board[y][n-y] == 1:
          if last != 1:
            count = 0
          last = 1
          count+=1
        if count == 4:
          return last
        
  return 0

def connect_four():
  board = [[0 for x in range(7)] for y in range(6)]
  xheight = [5 for x in range(7)]
  turn_piece = 1
  while winner(board) == 0 and not all(piece != 0 for piece in board[0]):
    for i in range(6):
      print(board[i])
    while True:
      try:
        move = int(input("Input the column you want to place your move: "))
        if xheight[move] >= 0 and move >= 0:
          break
        print("Invalid move")
      except:
        print("Invalid move")
    board[xheight[move]][move] = turn_piece
    xheight[move] -= 1
    if turn_piece == 1:
      turn_piece = -1
    else:
      turn_piece = 1
  for i in range(6):
      print(board[i])
  if winner(board) == 0:
    print("Draw")
  else:
    print("The winner is " + str(winner(board)))