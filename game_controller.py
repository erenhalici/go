
from board_converter import *

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
          if event.type == pygame.MOUSEBUTTONDOWN:
            board = convert_board(self._game)
            layer = 31
            print board.size
            print board.shape
            print board.transpose((2,0,1))[layer]
            packed = np.packbits(board)
            print packed
            print packed.size
            print packed.shape
            new_board = np.unpackbits(packed)[:(19*19*32)].reshape((19,19,32))
            print new_board.size
            print new_board.shape
            print new_board.transpose((2,0,1))[layer]

  def show_game(self, sgf_game):
    for (game, move) in sgf_game.all_positions():
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          return

      self._game_view.game = game
      self._game_view.draw()

      board = convert_board(game)
      print board.transpose((2,0,1))[0]

      pygame.time.wait(5000)

    while True:
      pygame.time.wait(250)
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          return
        else:
          self._game_view.event(event)

      game.invert_sides()
      self._game_view.draw()

  def make_move(self, x, y):
    if self._game.make_move(x, y):
      # (new_x, new_y) = Bridge.make_move(self._game)
      # self._game_view.draw()
      # pygame.time.wait(250)
      # self._game.make_move(new_x, new_y)
      self._game_view.draw()
