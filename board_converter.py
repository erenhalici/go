import numpy as np
from numpy import zeros

from game import *

def invert_board(board):
  new_board = zeros((19, 19), dtype=str)

  for row in range(19):
    for col in range(19):
      e = board[row][col]
      if e == BLACK:
        new_board[row][col] = WHITE
      elif e == WHITE:
        new_board[row][col] = BLACK
      else:
        new_board[row][col] = e

  return new_board


def convert_board(game):
  new_board = zeros((19, 19, 8), dtype=np.uint8)

  score = (game.lost_pieces - game.komi + 6.5) * 2
  board = game._board

  if game.current_player:
    board = invert_board(board)
    score = -score



  for row in range(19):
    for col in range(19):
      lost_b = 1 if count < lost_count_b else 0
      lost_w = 1 if count < lost_count_w else 0
      k      = 1 if count < komi         else 0

      count += 1

      e = board[row][col]

      if   e == BLACK: new_board[row][col] = [1, 0, 0, 0, lost_b, lost_w, k, player]
      elif e == WHITE: new_board[row][col] = [0, 1, 0, 0, lost_b, lost_w, k, player]
      elif e == KO:    new_board[row][col] = [0, 0, 1, 0, lost_b, lost_w, k, player]
      else:            new_board[row][col] = [0, 0, 0, 1, lost_b, lost_w, k, player]

  return new_board