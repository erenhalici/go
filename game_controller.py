
from game_view import *
from game import *
from bridge import *

class GameController(object):
  def __init__(self):
    self._game = Game()
    self._game_view = GameView(self, self._game)

  def run(self):
    while True:
      pygame.time.wait(30)
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          return
        else:
          self._game_view.event(event)

  def make_move(self, x, y):
    if self._game.make_move(x, y):
      (new_x, new_y) = Bridge.make_move(self._game)
      self._game.make_move(new_x, new_y)
      self._game_view.draw()

