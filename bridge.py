
import numpy as np
from numpy import zeros

from game import *
from predict_move import *

class Bridge:
  @classmethod
  def make_move(cls, game):
    board = cls.convert_board(game)
    legal = cls.legal_moves(game)

    if legal == None:
      return None
    else:
      return predict_move(board, legal, game.current_player)

  @classmethod
  def legal_moves(cls, game):
    legal_moves = zeros((19,19), dtype=np.uint8)

    found_legal = False

    for row in range(19):
      for col in range(19):
        if game.is_legal(row, col):
          legal_moves[row][col] = 1
          found_legal = True

    if found_legal:
      return legal_moves
    else:
      return None


  @classmethod
  def convert_board(cls, game):
    new_board = zeros((19, 19, 8), dtype=np.uint8)

    board = game._board
    lost_pieces = game.lost_pieces
    komi = game.komi

    player = 1 if game.current_player else 0

    count = 0

    if lost_pieces < 0:
      lost_count_b = 0
      lost_count_w = -lost_pieces
    else:
      lost_count_b = lost_pieces
      lost_count_w = 0

    komi = komi * 2

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
