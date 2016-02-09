#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

FREE  = 0
BLACK = 1
WHITE = 2
KO    = 3

class Game(object):
  def __init__(self):
    self._current_player = False
    self._board = np.zeros((19, 19), dtype=int)

    self._liberties = np.zeros((19, 19), dtype=int)
    self.update_all_liberties()

    self._komi = 6.5
    self._lost_pieces = 0

    self._last_ko = None

    for row in range(19):
      for col in range(19):
        self._board[row][col] = FREE

  @property
  def komi(self):
    return self._komi

  @komi.setter
  def komi(self, komi):
    self._komi = komi

  @property
  def lost_pieces(self):
    return self._lost_pieces

  @property
  def board(self):
    return self._board

  @board.setter
  def board(self, board):
    self._board = board

  @property
  def liberties(self):
    return self._liberties

  @property
  def current_player(self):
    return self._current_player

  def adjacencies(self, row, col):
    adj = set()

    if row > 0:  adj.add((row-1, col))
    if row < 18: adj.add((row+1, col))
    if col > 0:  adj.add((row, col-1))
    if col < 18: adj.add((row, col+1))

    return adj


  def get_group(self, row, col):
    group = set()
    queue = set()

    my_type = self._board[row][col]
    if my_type == BLACK or my_type == WHITE:
      queue.add((row, col))

    while queue:
      (r, c) = queue.pop()
      if self._board[r][c] == my_type:
        group.add((r, c))

        for adj in self.adjacencies(r, c):
          if adj not in group:
            queue.add(adj)

    return group

  def group_size(self, row, col):
    my_type = self._board[row][col]
    if my_type == FREE or my_type == KO:
      return 0

    visited = set()
    queue = set()
    queue.add((row, col))

    count = 0

    while queue:
      (r, c) = queue.pop()
      visited.add((r, c))

      if self._board[r][c] == my_type:
        count += 1
        for adj in self.adjacencies(r, c):
          if adj not in visited:
            queue.add(adj)

    return count

  def update_all_liberties(self):
    for row in range(19):
      for col in range(19):
        self._liberties[row][col] = self.num_liberties(row, col)

  def update_liberties(self, row, col):
    my_type = self._board[row][col]

    if my_type == BLACK:
      opponent_type = WHITE
    elif my_type == WHITE:
      opponent_type = BLACK
    else:
      return

    l = self.num_liberties(row, col)
    for (r, c) in self.get_group(row, col):
      self._liberties[r][c] = l

    opponent_group = set()

    for (r, c) in self.adjacencies(row, col):
      if self._board[r][c] == opponent_type:
        opponent_group |= self.get_group(r, c)
    for (r, c) in opponent_group:
      self._liberties[r][c] -= 1

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
        for adj in self.adjacencies(r, c):
          if adj not in visited:
            queue.add(adj)

    return liberties

  def num_captures(self, row, col):
    if self._board[row][col] != FREE:
      return 0

    opponent_type = BLACK if self._current_player else WHITE
    captures = 0

    captured = set()

    for adj in self.adjacencies(row, col):
      (r, c) = adj
      if self.board[r][c] == opponent_type and self.liberties[r][c] == 1:
        captured |= self.get_group(r, c)

    return len(captured)


  def remove_group(self, row, col):
    my_type = self._board[row][col]
    if my_type == FREE or my_type == KO:
      return 0

    captured = 0

    visited = set()
    queue = set()
    queue.add((row, col))

    while queue:
      (r, c) = queue.pop()
      visited.add((r, c))
      if self._board[r][c] == my_type:
        self._board[r][c] = FREE
        captured += 1

        for adj in self.adjacencies(r, c):
          if adj not in visited:
            queue.add(adj)

    return captured

  def remove_captured(self, row, col):
    opponent_type = BLACK if self._current_player else WHITE

    captured = 0

    for adj in self.adjacencies(row, col):
      (r, c) = adj
      if self.board[r][c] == opponent_type and self.num_liberties(r, c) == 1:
        captured += self.remove_group(r, c)

    return captured

  def is_legal(self, row, col):
    if not 0 <= row < 19 or not 0 <= col < 19:
      return False

    if self._board[row][col] != FREE:
      return False

    opponent_type = BLACK if self._current_player else WHITE

    for (r, c) in self.adjacencies(row, col):
      e = self.board[r][c]
      if e == FREE or e == KO:
        return True
      elif e == opponent_type:
        if self.liberties[r][c] == 1:
          return True
      else:  # e == my_type
        if self.liberties[r][c] != 1:
          return True

    return False

  def skip_move(self):
    self._current_player = not self._current_player

  def make_move(self, row, col):
    if (row, col) == (-1, -1):
      self.skip_move()
      return True

    if not self.is_legal(row, col):
      return False

    board = self._board

    if self._last_ko != None:
      board[self._last_ko[0]][self._last_ko[1]] = FREE
      self._last_ko = None

    captured = self.remove_captured(row, col)

    if (self._current_player):
      self._lost_pieces -= captured
      board[row][col] = WHITE
    else:
      self._lost_pieces += captured
      board[row][col] = BLACK

    if captured == 0:
      self.update_liberties(row, col)
    else:
      self.update_all_liberties()

    if captured == 1 and self.num_liberties(row, col) == 1 and self.group_size(row, col) == 1:
      for adj in self.adjacencies(row, col):
        (r, c) = adj
        if board[r, c] == FREE:
          board[r][c] = KO
          self._last_ko = (r, c)

    self.skip_move()

    return True


  def evaluate(self):
    score = self._lost_pieces - self._komi

    board = self._board

    for row in range(19):
      for col in range(19):
        if board[row][col] == FREE:
          blacks = 0
          whites = 0
          for adj in self.adjacencies(row, col):
            tile = board[adj[0], adj[1]]
            if tile == BLACK:
              blacks += 1
            elif tile == WHITE:
              whites += 1
          if blacks == 4:
            score += 1
          elif whites == 4:
            score -= 1

    return score

  def invert_sides(self):
    for row in range(19):
      for col in range(19):
        e = self._board[row][col]
        if e == BLACK:
          self._board[row][col] = WHITE
        elif e == WHITE:
          self._board[row][col] = BLACK
        else:
          self._board[row][col] = e

    self._komi        = -self._komi
    self._lost_pieces  = -self._lost_pieces

    self._current_player = not self._current_player
