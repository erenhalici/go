import numpy as np

from game import *

# 0   State: BLACK
# 1   State: WHITE
# 2   State: KO
# 3   State: FREE
# 4   Liberty Black: 1
# 5   Liberty Black: 2
# 6   Liberty Black: 3
# 7   Liberty Black: 4+
# 8   Liberty White: 1
# 9   Liberty White: 2
# 10  Liberty White: 3
# 11  Liberty White: 4+
# 12  Captures: 1
# 13  Captures: 2
# 14  Captures: 3
# 15  Captures: 4+
# 16  Score: (-3)-
# 17  Score: -2
# 18  Score: -1
# 19  Score: 0
# 20  Score: 1
# 21  Score: 2
# 22  Score: 3+
# 23  Komi: 5.5
# 24  Komi: 6.5
# 25  Komi: 7.5
# 26  Komi: -5.5
# 27  Komi: -6.5
# 28  Komi: -7.5
# 29  Move Legality
# 30  1
# 31  0

def convert_board(game):
  new_board = np.zeros((19, 19, 32), dtype=int)

  inverted = False

  if game.current_player:
    game.invert_sides()
    inverted = True

  komi = game.komi
  score = game.lost_pieces
  board = game.board

  for row in range(19):
    for col in range(19):
      b = new_board[row][col]

      e = board[row][col]

      if e == BLACK:
        b[0] = 1
      elif e == WHITE:
        b[1] = 1
      elif e == KO:
        b[2] = 1
      elif e == FREE:
        b[3] = 1
      else:
        raise Exception("Unknown state: %s"%e)

      if e == BLACK:
        black_liberties = game.liberties[row][col]
        if black_liberties == 0:
          raise Exception("Zero liberty stone found!")
      else:
        black_liberties = 0

      if black_liberties == 1:
        b[4] = 1
      elif black_liberties == 2:
        b[5] = 1
      elif black_liberties == 3:
        b[6] = 1
      elif black_liberties >= 4:
        b[7] = 1

      if e == WHITE:
        white_liberties = game.liberties[row][col]
        if white_liberties == 0:
          raise Exception("Zero liberty stone found!")
      else:
        white_liberties = 0

      if white_liberties == 1:
        b[8] = 1
      elif white_liberties == 2:
        b[9] = 1
      elif white_liberties == 3:
        b[10] = 1
      elif white_liberties >= 4:
        b[11] = 1

      captures = game.num_captures(row, col)
      if captures == 1:
        b[12] = 1
      elif captures == 2:
        b[13] = 1
      elif captures == 3:
        b[14] = 1
      elif captures >= 4:
        b[15] = 1

      # if e == FREE:
      #   game._board[row][col] = BLACK
      #   liberties_after = game.num_liberties(row, col)

      #   if not captures == 0:
      #     for (r, c) in game.adjacencies(row, col):
      #       if game.board[r, c] == WHITE and game.liberties[r][c] == 1:
      #         liberties_after += 1

      #   game._board[row][col] = e
      # else:
      #   liberties_after = 0
      # if liberties_after > 4:
      #   liberties_after = 4
      # liberties_after = dense_to_one_hot(liberties_after-1, 4)

      if score <= -3:
        b[16] = 1
      elif score == -2:
        b[17] = 1
      elif score == -1:
        b[18] = 1
      elif score == 0:
        b[19] = 1
      elif score == 1:
        b[20] = 1
      elif score == 2:
        b[21] = 1
      elif score >= 3:
        b[22] = 1

      if komi == 5.5:
        b[23] = 1
      elif komi == 6.5:
        b[24] = 1
      elif komi == 7.5:
        b[25] = 1
      elif komi == -5.5:
        b[26] = 1
      elif komi == -6.5:
        b[27] = 1
      elif komi == -7.5:
        b[28] = 1
      else:
        raise Exception("Komi other than 5.5, 6.5 or 7.5 is not supported. Current komi is %f"%game.komi)

      if game.is_legal(row, col):
        b[29] = 1

      b[30] = 1

  if inverted:
    game.invert_sides()

  return new_board