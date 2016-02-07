import datetime
import math
import h5py

from board_converter import *

import pygame
from sys import exit
from game_controller import GameController

import fnmatch
import os

from datetime import datetime

from sgf_game import SGFGame


game_controller = GameController()


def game_filter(game):
  metadata = game.metadata

  if 'size' in metadata and metadata['size'] != 19:
    return False

  if 'date' in metadata and metadata['date'].year < 1900:
    return False

  if 'handicap' in metadata and not handicap == 0:
    return False

  # if 'komi' in metadata and not (metadata['komi'] * 2).is_integer():
  #   return False
  if not 'komi' in metadata or (not metadata['komi'] == 6.5 and not metadata['komi'] == 7.5 and not metadata['komi'] == 5.5):
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
pos_count = 0

output_file = h5py.File("data/training/36_layer.hdf5", "w")
data_size = int(math.ceil(19*19*36/8.0))
data_count = 100000
dset = output_file.create_dataset("positions", (data_count, data_size), maxshape=(None, data_size), dtype=np.uint8)

for root, dirnames, filenames in os.walk('./data/games/'):
  for filename in fnmatch.filter(filenames, '*.sgf'):

    file = os.path.join(root, filename)
    # print (file)
    # print open(file).read()

    try:
      sgf_game = SGFGame(file)
      if game_filter(sgf_game):
        sgf_game.extract_moves()

        for game in sgf_game.all_positions():
          # board = np.packbits(convert_board(game))
          convert_board(game)

        # game_controller.show_game(sgf_game)

          # if pos_count == data_count:
          #   print "Increasing data_size: %i"%pos_count
          #   data_count += 100000
          #   dset.resize(data_count, 0)
          #   print "Done"
          # dset[pos_count] = board
          pos_count += 1
          if pos_count % 1000 == 0:
            print pos_count
            print datetime.now().time()

        count += 1
    except Exception, e:
      print str(total) + ": " + str(e)
      # pass
    else:
      pass
    finally:
      pass

    total += 1

    # print total


print str(count) + ' out of ' + str(total) + ' games are eligible'
print 'A total of ' + str(pos_count) + ' positions'