
import multiprocessing as mp

import time
import math
import h5py

from board_converter import *

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

  # if 'komi' in metadata and not (metadata['komi'] * 2).is_integer():
  #   return False
  if not 'komi' in metadata or (not metadata['komi'] == 6.5 and not metadata['komi'] == 7.5 and not metadata['komi'] == 5.5):
    return False

  if 'white_rank' in metadata:
    if not 'white_dan' in metadata or metadata['white_dan'] < 7:
      return False

  if 'black_rank' in metadata:
    if not 'black_dan' in metadata or metadata['black_dan'] < 7:
      return False

  return True

total = 0
count = 0
pos_count = 0
games_set = set()

data_file = h5py.File("data/training/32_layers.hdf5", "w")
# label_file    = h5py.File("data/training/labels.hdf5", "w")

position_data_size = int(math.ceil(19*19*32/8.0))
label_data_size = int(math.ceil(362/8.0))
data_count = 100000
positions = data_file.create_dataset("positions", (data_count, position_data_size), maxshape=(None, position_data_size), dtype=np.uint8)
labels    = data_file.create_dataset("labels", (data_count, label_data_size), maxshape=(None, label_data_size), dtype=np.uint8)

start_time = time.time()

def convert_position(position):
  (game, (row, col)) = position

  label = np.zeros(362, dtype=int)
  if row == -1 or col == -1:
    label[361] = 1
  else:
    label[row * 19 + col] = 1

  return (np.packbits(convert_board(game)), np.packbits(label))

core_count = mp.cpu_count()
print "Working on %d cores"%core_count
pool = mp.Pool(core_count)

for root, dirnames, filenames in os.walk('./data/games/'):
  for filename in fnmatch.filter(filenames, '*.sgf'):
    if pos_count < 10000:
      file = os.path.join(root, filename)

      try:
        sgf_game = SGFGame(file)
        if game_filter(sgf_game):
          sgf_game.extract_moves()
          moves_hash = sgf_game.moves_hash()
          if moves_hash not in games_set:
            games_set.add(moves_hash)
            # game_controller.show_game(sgf_game)

            converted = pool.map(convert_position, sgf_game.all_positions())

            for (board, label) in converted:
              if pos_count == data_count:
                print "Increasing data_size: %i"%pos_count
                data_count += 100000
                positions.resize(data_count, 0)
                labels.resize(data_count, 0)
                print "Done"

              positions[pos_count] = board
              labels[pos_count] = label

              pos_count += 1
              if pos_count % 1000 == 0:
                print pos_count
                print "%f positions per hour"%(pos_count/(time.time() - start_time) * 3600)
                print "Approximately %f hours to end"%(8404613.0/pos_count*(time.time() - start_time)/3600)

            count += 1
      except Exception, e:
        print str(total) + ": " + str(e)
      else:
        pass
      finally:
        pass

      total += 1

pool.close()

print str(count) + ' out of ' + str(total) + ' games are eligible'
print 'A total of ' + str(pos_count) + ' positions'

positions.attrs['count'] = pos_count
positions.attrs['layers'] = 32
labels.attrs['count'] = pos_count
labels.attrs['classes'] = 362
data_file.close()