#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import zeros

FREE  = 'a'
BLACK = '.'
WHITE = 'o'

class Game:
  def __init__(self):
    self._current_player = False
    self._board = zeros((19, 19), dtype=unicode)


    for row in range(19):
      for col in range(19):
        self._board[row][col] = FREE

  @property
  def board(self):
      return self._board

  def make_move(self, row, col):
    if not 0 <= row < 19 or not 0 <= col < 19:
      return False

    if self._board[row][col] != FREE:
      return False

    self._board[row][col] = WHITE if (self._current_player) else BLACK
    self._current_player = not self._current_player

    return True