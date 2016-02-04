
# import pygame
# from sys import exit
# from game_controller import GameController

import fnmatch
import os

from datetime import datetime

from sgf_game import SGFGame


# game_controller = GameController()


def game_filter(game):
  metadata = game.metadata

  if 'size' in metadata and metadata['size'] != 19:
    return False

  if 'date' in metadata and metadata['date'].year < 1900:
    return False

  if 'handicap' in metadata and not handicap == 0:
    return False

  if 'komi' in metadata and not (metadata['komi'] * 2).is_integer():
    return False

  if 'white_rank' in metadata:
    if not 'white_dan' in metadata or metadata['white_dan'] < 8:
      return False

  if 'black_rank' in metadata:
    if not 'black_dan' in metadata or metadata['black_dan'] < 8:
      return False

  return True

total = 0
count = 0
for root, dirnames, filenames in os.walk('./data/games/'):
  for filename in fnmatch.filter(filenames, '*.sgf'):

    file = os.path.join(root, filename)
    # print (file)
    # print open(file).read()

    try:
      sgf_game = SGFGame(file)
      if game_filter(sgf_game):
        sgf_game.extract_moves()

        # for game in sgf_game.all_positions():
          # print game.board

        # game_controller.show_game(sgf_game)


        count += 1
    except Exception, e:
      print str(total) + ": " + str(e)
    else:
      pass
    finally:
      pass

    total += 1

    # print total


print str(count) + ' out of ' + str(total) + ' games are eligible'