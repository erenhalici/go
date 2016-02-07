import numpy as np

from game import *

def dense_to_one_hot(label, num_classes):
  label_one_hot = np.zeros(num_classes, dtype=np.uint8)

  if label < 0 or label >= num_classes:
    return label_one_hot

  label_one_hot[label] = 1
  return label_one_hot

def convert_board(game):
  new_board = np.zeros((19, 19, 36), dtype=np.uint8)

  inverted = False
  if game.current_player:
    game.invert_sides()
    inverted = True

  if game.komi == 5.5:
    komi = 0
  elif game.komi == 6.5:
    komi = 1
  elif game.komi == 7.5:
    komi = 2
  elif game.komi == -5.5:
    komi = 3
  elif game.komi == -6.5:
    komi = 4
  elif game.komi == -7.5:
    komi = 5
  else:
    raise Exception("Komi other than 5.5, 6.5 or 7.5 is not supported. Current komi is %f"%game.komi)
  komi = dense_to_one_hot(komi, 6)

  score = game.lost_pieces
  if score < -3:
    score = -3
  elif score > 3:
    score = 3
  score = dense_to_one_hot(score + 3, 7)

  board = game._board

  for row in range(19):
    for col in range(19):
      e = board[row][col]

      if e == BLACK:
        state = 0
      elif e == WHITE:
        state = 1
      elif e == KO:
        state = 2
      elif e == FREE:
        state = 3
      else:
        raise Exception("Unknown state: %s"%e)
      state = dense_to_one_hot(state, 4)


      if e == BLACK:
        black_liberties = game.num_liberties(row, col)
        if black_liberties == 0:
          raise Exception("Zero liberty stone found!")
      else:
        black_liberties = 0
      if black_liberties > 4:
        black_liberties = 4
      black_liberties = dense_to_one_hot(black_liberties-1, 4)

      if e == WHITE:
        white_liberties = game.num_liberties(row, col)
        if white_liberties == 0:
          raise Exception("Zero liberty stone found!")
      else:
        white_liberties = 0
      if white_liberties > 4:
        white_liberties = 4
      white_liberties = dense_to_one_hot(white_liberties-1, 4)

      if e == FREE:
        game._board[row][col] = BLACK
        liberties_after = game.num_liberties(row, col)

        for (r, c) in game.adjacencies(row, col):
          if game.num_liberties(r, c) == 0:
            liberties_after += 1
      else:
        liberties_after = 0
      if liberties_after > 4:
        liberties_after = 4
      liberties_after = dense_to_one_hot(liberties_after-1, 4)
      game._board[row][col] = e

      captures = game.num_captures(row, col)
      if captures > 4:
        captures = 4
      captures = dense_to_one_hot(captures-1, 4)

      # captures = black_liberties = white_liberties = liberties_after = [0,0,0,0]

      legal = 1 if game.is_legal(row, col) else 0
      one = 1
      zero = 0

      new_board[row][col] = np.concatenate((state, black_liberties, white_liberties, liberties_after, captures, score, komi, [legal, one, zero]))

  if inverted:
    game.invert_sides()

  return new_board