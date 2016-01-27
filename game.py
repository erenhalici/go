#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import zeros

FREE  = ' '
BLACK = '.'
WHITE = 'o'
KO    = 'x'

class Game:
  def __init__(self):
    self._current_player = False
    self._board = zeros((19, 19), dtype=unicode)

    self._komi = 6.5
    self._lost_pieces = 0

    for row in range(19):
      for col in range(19):
        self._board[row][col] = FREE

  @property
  def komi(self):
      return self._komi

  @property
  def lost_pieces(self):
      return self._lost_pieces

  @property
  def board(self):
      return self._board

  @property
  def current_player(self):
      return self._current_player

  def num_liberties(self, row, col):
    my_type = self._board[row][col]

    liberties = 0

    visited = set()
    queue = set()
    queue.add((row, col))

    while queue:
      (r, c) = queue.pop()
      visited.add((r, c))

      if self._board[r][c] == FREE or self._board[r][c] == KO:
        liberties += 1
      elif self._board[r][c] == my_type:
        if r > 0  and (r-1, c) not in visited: queue.add((r-1, c))
        if r < 18 and (r+1, c) not in visited: queue.add((r+1, c))
        if c > 0  and (r, c-1) not in visited: queue.add((r, c-1))
        if c < 18 and (r, c+1) not in visited: queue.add((r, c+1))

    return liberties

  def remove_group(self, row, col):
    my_type = self._board[row][col]
    if my_type == FREE or my_type == KO:
      return

    captured = 0

    visited = set()
    queue = set()
    queue.add((row, col))

    while queue:
      (r, c) = queue.pop()
      visited.add((r, c))
      if self._board[r][c] == my_type:
        self._board[r][c] = FREE

        if r > 0  and (r-1, c) not in visited: queue.add((r-1, c))
        if r < 18 and (r+1, c) not in visited: queue.add((r+1, c))
        if c > 0  and (r, c-1) not in visited: queue.add((r, c-1))
        if c < 18 and (r, c+1) not in visited: queue.add((r, c+1))

  def remove_captured(self, row, col):
    opponent_type = BLACK if self._current_player else WHITE

    if row > 0  and self._board[row-1][col] == opponent_type and self.num_liberties(row-1, col) == 1: self.remove_group(row-1, col)
    if row < 18 and self._board[row+1][col] == opponent_type and self.num_liberties(row+1, col) == 1: self.remove_group(row+1, col)
    if col > 0  and self._board[row][col-1] == opponent_type and self.num_liberties(row, col-1) == 1: self.remove_group(row, col-1)
    if col < 18 and self._board[row][col+1] == opponent_type and self.num_liberties(row, col+1) == 1: self.remove_group(row, col+1)

  def is_legal(self, row, col):
    if not 0 <= row < 19 or not 0 <= col < 19:
      return False

    if self._board[row][col] != FREE:
      return False

    opponent_type = BLACK if self._current_player else WHITE

    if row > 0  and self._board[row-1][col] == opponent_type and self.num_liberties(row-1, col) == 1: return True
    if row < 18 and self._board[row+1][col] == opponent_type and self.num_liberties(row+1, col) == 1: return True
    if col > 0  and self._board[row][col-1] == opponent_type and self.num_liberties(row, col-1) == 1: return True
    if col < 18 and self._board[row][col+1] == opponent_type and self.num_liberties(row, col+1) == 1: return True

    self._board[row][col] = WHITE if (self._current_player) else BLACK
    lib = self.num_liberties(row, col)
    self._board[row][col] = FREE

    return lib != 0

  def make_move(self, row, col):
    if not self.is_legal(row, col): return False

    self.remove_captured(row, col)
    self._board[row][col] = WHITE if (self._current_player) else BLACK

    self._current_player = not self._current_player

    return True
