from game import Game
from dateutil import parser
import copy

class SGFGame():
  def __init__(self, filename):
    f = open(filename)
    # f = ''.join(f.split())
    tokens = f.read().split(';')
    f.close()
    tokens.pop(0)
    info = tokens.pop(0)
    self.extract_metadata(info, filename)

    self._tokens = tokens
    self._filename = filename
    self._moves = []

  @property
  def metadata(self):
      return self._metadata

  @property
  def moves(self):
      return self._moves


  def moves_hash(self):
    return hash(str(self._moves))

  def extract_metadata(self, info, filename):
    metadata = {}

    for pair in info.split(']'):
      if pair.strip() == '':
        continue

      k, v = [x.strip() for x in pair.split('[')]

      if k == 'SZ':
        metadata['size'] = int(v)
      elif k == 'PB':
        metadata['black_player'] = v
      elif k == 'PW':
        metadata['white_player'] = v
      elif k == 'RE':
        metadata['result'] = v
      elif k == 'KM':
        metadata['komi'] = float(v)
      elif k == 'BR':
        metadata['black_rank'] = v
        dan = v.split('p')
        if len(dan) == 1:
          dan = v.split('d')
        if len(dan) > 1:
          metadata['black_dan'] = int(dan[0])
      elif k == 'WR':
        metadata['white_rank'] = v
        dan = v.split('p')
        if len(dan) == 1:
          dan = v.split('d')
        if len(dan) > 1:
          metadata['white_dan'] = int(dan[0])
      elif k == 'OT':
        metadata['overtime'] = v
      elif k == 'PC':
        metadata['place'] = v
      elif k == 'TM':
        metadata['time_limit'] = v
      elif k == 'RU':
        metadata['rule_set'] = v
      elif k == 'FF':
        if v != '4' and v != '3':
          raise Exception("Unknown File Format: %s" % v)
      elif k == 'CA':
        metadata['encoding'] = v
      elif k == 'DT':
        try:
          metadata['date'] = parser.parse(v.split(',')[0])
        except Exception, e:
          pass
      elif k == 'HA':
        metadata['handicap'] = int(v)
      elif k == 'AB' or k == 'AW':
        raise Exception('Adding stones are unsupported!')
      elif k == 'GM':
        if v != '1':
          raise Exception("Unknown Game Type: %s" % v)
      elif k == 'RO':
        metadata['round'] = v
      elif k == 'EV':
        metadata['event'] = v
      elif k == 'WT':
        metadata['white_team'] = v
      elif k == 'BT':
        metadata['black_team'] = v
      elif k == 'GC':
        metadata['game_comment'] = v
      elif k == 'C':
        metadata['comment'] = v
      elif k == 'AP' or k == 'ST' or k == 'US' or k == 'SO' or k == 'GN':
        pass
      else:
        pass
        # print "Unknown key: " + k + " with value: " + v

      self._metadata = metadata

  def extract_moves(self):
    last_player = 'W'
    while self._tokens:
      move = self._tokens.pop(0).upper().strip()

      if '(' in move:
        raise Exception("Games with alternate lines are not supported")

      player = move.split('[')[0]

      if player == 'W' or player == 'B':
        if last_player == player:
          raise Exception("Multiple moves from same player")

        move = move.split('[')[1].split(']')[0]

        if len(move) == 0:
          location = (-1, -1)
        elif move == 'TT':
          location = (-1, -1)
        else:
          location = (ord(move[1]) - ord('A'), ord(move[0]) - ord('A'))

        self._moves.append(location)

        last_player = player

      elif player == 'C' or player == ')':
        pass
      else:
        raise Exception("Unknown token %s"%move)

    self.add_passing_moves()

  def add_passing_moves(self):
    if 'result' in self._metadata:
      result = self._metadata['result']

      f = result.partition('+')[2]

      try:
        float(f)
      except Exception, e:
        pass
      else:
        while not self._moves[-2] == (-1, -1):
          self._moves.append((-1, -1))

  def all_positions(self):
    game = Game()

    if 'komi' in self._metadata:
      game.komi = self._metadata['komi']
    else:
      game.komi = 0

    for move in self.moves:
      if move != (-1, -1):
        yield copy.deepcopy(game), move
      row, col = move
      if not game.make_move(row, col):
        raise Exception("WRONG MOVE!!!!!!!")
