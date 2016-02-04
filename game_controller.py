
from game_view import *
from game import *
from bridge import *
from sgf_game import SGFGame

class GameController(object):
  def __init__(self):
    self._game = Game()
    self._game_view = GameView(self, self._game)

  def sim(self):
    running = True
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          return

      if running:
        move = Bridge.make_move(self._game)
        if move == None:
          print self._game.evaluate()
          running = False
        else:
          (new_x, new_y) = move
          self._game.make_move(new_x, new_y)
          self._game_view.draw()

      pygame.time.wait(30)

  def run(self):
    while True:
      pygame.time.wait(30)
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          return
        else:
          self._game_view.event(event)

  def show_game(self, sgf_game):
    for game in sgf_game.all_positions():
      pygame.time.wait(25)

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          return

      self._game_view.game = game
      self._game_view.draw()

    while True:
      pygame.time.wait(30)
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          return
        else:
          self._game_view.event(event)



  def make_move(self, x, y):
    if self._game.make_move(x, y):
      # (new_x, new_y) = Bridge.make_move(self._game)
      # self._game_view.draw()
      # pygame.time.wait(250)
      # self._game.make_move(new_x, new_y)
      self._game_view.draw()
