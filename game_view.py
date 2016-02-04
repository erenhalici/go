
import pygame

from game import *

BOARD_SIZE = (820, 820)
WHITE_COLOR = (240, 240, 240)
BACKGROUND  = (192, 164, 128)
BLACK_COLOR = (32, 32, 32)

class GameView(object):
  def __init__(self, game_controller, game):
    pygame.init()
    pygame.display.set_caption('Neural Go')

    self._game_controller = game_controller
    self._game = game

    self._screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)
    self._outline = pygame.Rect(45, 45, 720, 720)
    self.draw()

  @property
  def game(self):
    return self._game

  @game.setter
  def game(self, game):
    self._game = game

  def draw(self):
    rect = pygame.Rect(0, 0, BOARD_SIZE[0], BOARD_SIZE[1])
    pygame.draw.rect(self._screen, BACKGROUND, rect, 0)
    self._outline.inflate_ip(20, 20)
    for i in range(18):
      for j in range(18):
        rect = pygame.Rect(45 + (40 * i), 45 + (40 * j), 40, 40)
        pygame.draw.rect(self._screen, BLACK_COLOR, rect, 1)
    for i in range(3):
      for j in range(3):
        coords = (165 + (240 * i), 165 + (240 * j))
        pygame.draw.circle(self._screen, BLACK_COLOR, coords, 5, 0)
    for row in range(19):
      for col in range(19):
        stone = self._game.board[row][col]
        if stone == BLACK or stone == WHITE:
          self.draw_stone(row, col, stone)
    pygame.display.update()

  def draw_stone(self, row, col, stone):
    coords = (5 + (col+1) * 40, 5 + (row+1) * 40)
    color = BLACK_COLOR if (stone == BLACK) else WHITE_COLOR
    pygame.draw.circle(self._screen, color, coords, 20, 0)

  def event(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
      if event.button == 1:
        row = int(round(((event.pos[1] - 5) / 40.0), 0)) - 1
        col = int(round(((event.pos[0] - 5) / 40.0), 0)) - 1
        self._game_controller.make_move(row, col)