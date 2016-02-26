
# import multiprocessing as mp
import numpy as np
import h5py

class DataSet(object):
  def __init__(self, positions, labels, num_positions, num_layers, num_classes):
    self._num_positions = num_positions*8
    self._num_layers = num_layers
    self._num_classes = num_classes

    self._positions = positions
    self._labels = labels
    self._epochs_completed = 0
    self._index_in_epoch = 0

    self._indices = np.arange(self._num_positions)
    # self._pool = mp.Pool(mp.cpu_count())

  @property
  def positions(self):
    return self._positions
  @property
  def labels(self):
    return self._labels
  @property
  def num_positions(self):
    return self._num_positions
  @property
  def num_layers(self):
    return self._num_layers
  @property
  def num_classes(self):
    return self._num_classes
  @property
  def epochs_completed(self):
    return self._epochs_completed
  def epoch(self):
    return self._epochs_completed + self._index_in_epoch*1.0/self._num_positions
  def convert_position(self, position):
    return np.unpackbits(position)[:19*19*self._num_layers].reshape(19,19,self._num_layers)
  def convert_label(self, label):
    return np.unpackbits(label)[:self._num_classes].reshape(19,19)
  def all_positions(self):
    return [self.convert_position(position) for position in self._positions]
  def all_labels(self):
    return [self.convert_label(label).reshape(-1) for label in self._labels]
  def augment_position(self, position, index):
    i = index%8

    if i == 0:
      return np.rot90(position)
    elif i == 1:
      return np.rot90(position,2)
    elif i == 2:
      return np.rot90(position,3)
    elif i == 3:
      return position
    elif i == 4:
      return np.fliplr(position)
    elif i == 5:
      return np.flipud(position)
    elif i == 6:
      return position.transpose(1,0,2)
    elif i == 7:
      return np.fliplr(np.rot90(position))
  def augment_label(self, label, index):
    i = index%8

    if i == 0:
      return np.rot90(label)
    elif i == 1:
      return np.rot90(label,2)
    elif i == 2:
      return np.rot90(label,3)
    elif i == 3:
      return label
    elif i == 4:
      return np.fliplr(label)
    elif i == 5:
      return np.flipud(label)
    elif i == 6:
      return np.transpose(label)
    elif i == 7:
      return np.fliplr(np.rot90(label))
  def get_position_at_index(self, index):
    return self.augment_position(self.convert_position(self._positions[index/8]), index)
  def get_label_at_index(self, index):
    return self.augment_label(self.convert_label(self._labels[index/8]), index).reshape(361)
  def next_batch(self, batch_size):
    """Return the next `batch_size` examples from this data set."""
    start = self._index_in_epoch
    self._index_in_epoch += batch_size
    if self._index_in_epoch > self._num_positions:
      # Finished epoch
      self._epochs_completed += 1
      print("epoch {} completed".format(self._epochs_completed))
      # Shuffle the data
      np.random.shuffle(self._indices)
      # Start next epoch
      start = 0
      self._index_in_epoch = batch_size
      assert batch_size <= self._num_positions
    end = self._index_in_epoch

    indices = self._indices[start:end].tolist()
    indices.sort()
    # positions = [self.convert_position(position) for position in self._positions[indices]]
    # labels    = [self.convert_label(label)       for label    in self._labels[indices]]
    positions = [self.get_position_at_index(index) for index in indices]
    labels    = [self.get_label_at_index(index)    for index in indices]
    # positions = self._pool.map(self.get_position_at_index, indices)
    # labels    = self._pool.map(self.get_label_at_index,    indices)

    return positions, labels

def read_data_sets(data_file):
  class DataSets(object):
    pass
  data_sets = DataSets()

  # VALIDATION_SIZE = 20000
  TEST_SIZE = 10000

  # positions = extract_positions(os.path.join(train_dir, GAMES), num_input_layers)
  # labels = extract_labels(os.path.join(train_dir, RESULTS))

  f = h5py.File(data_file, 'r')
  positions = f['positions']
  labels = f['labels']

  num_positions = positions.attrs['count']
  num_layers = positions.attrs['layers']
  num_classes = labels.attrs['classes']

  positions = positions[:num_positions]
  labels = labels[:num_positions]

#  positions = numpy.concatenate((positions,positions[::-1,::-1,::-1,:]))
#  labels = numpy.vstack((labels, labels[::-1,::-1]))

#  train_positions = positions[TEST_SIZE:(positions.shape[0]-TEST_SIZE)]
#  train_labels = labels[TEST_SIZE:(labels.shape[0]-TEST_SIZE)]

#  test_positions = numpy.concatenate((positions[:TEST_SIZE], positions[(positions.shape[0]-TEST_SIZE):]))
#  test_labels = numpy.concatenate((labels[:TEST_SIZE], labels[(labels.shape[0]-TEST_SIZE):]))


  test_positions = positions[-TEST_SIZE:]
  test_labels = labels[-TEST_SIZE:]

  train_positions = positions[:-TEST_SIZE]
  train_labels = labels[:-TEST_SIZE]

  # data_sets.train = DataSet(train_positions, train_labels)
  # data_sets.test = DataSet(test_positions, test_labels)

  data_sets.train = DataSet(train_positions, train_labels, num_positions - TEST_SIZE, num_layers, num_classes)
  data_sets.test  = DataSet(test_positions,  test_labels, TEST_SIZE, num_layers, num_classes)

  return data_sets
