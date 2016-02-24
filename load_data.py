
import numpy as np
import h5py

class DataSet(object):
  def __init__(self, positions, labels, num_positions, num_layers, num_classes):
    self._num_positions = num_positions
    self._num_layers = num_layers
    self._num_classes = num_classes

    self._positions = positions
    self._labels = labels
    self._epochs_completed = 0
    self._index_in_epoch = 0

    self._indices = np.arange(self._num_positions)

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
    return np.unpackbits(label)[:self._num_classes]
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
    positions = [self.convert_position(position) for position in self._positions[indices]]
    labels    = [self.convert_label(label)       for label    in self._labels[indices]]

    return positions, labels

def read_data_sets(data_file):
  class DataSets(object):
    pass
  data_sets = DataSets()

  # VALIDATION_SIZE = 20000
  TEST_SIZE = 250000

  # positions = extract_positions(os.path.join(train_dir, GAMES), num_input_layers)
  # labels = extract_labels(os.path.join(train_dir, RESULTS))

  f = h5py.File(data_file, 'r')
  positions = f['positions']
  labels = f['labels']

  num_positions = positions.attrs['count']
  num_layers = positions.attrs['layers']
  num_classes = labels.attrs['classes']

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


  data_sets.train = DataSet(positions, labels, num_positions, num_layers, num_classes)
  return data_sets
