# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Functions for downloading and reading MNIST data."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import gzip
import os
import numpy
from six.moves import urllib
from six.moves import xrange  # pylint: disable=redefined-builtin

def _read32(bytestream):
  # dt = numpy.dtype(numpy.uint32)
  dt = numpy.dtype(numpy.uint32).newbyteorder('>')
  return numpy.frombuffer(bytestream.read(4), dtype=dt)[0]

def extract_images(filename):
  """Extract the images into a 4D uint8 numpy array [index, y, x, depth]."""
  print('Extracting', filename)
  with gzip.open(filename) as bytestream:
    num_images = _read32(bytestream)
    # num_images = 80000
    print(num_images)
    # rows = _read32(bytestream)
    # cols = _read32(bytestream)
    rows = 19
    cols = 19
    channels = 7
    buf = bytestream.read(rows * cols * num_images * channels)
    data = numpy.frombuffer(buf, dtype=numpy.uint8)
    print(data.size)
    data = data.reshape(num_images, rows, cols, channels)
    return data

def dense_to_one_hot(labels_dense, num_classes=2):
  """Convert class labels from scalars to one-hot vectors."""
  num_labels = labels_dense.shape[0]
  index_offset = numpy.arange(num_labels) * num_classes
  labels_one_hot = numpy.zeros((num_labels, num_classes))
  labels_one_hot.flat[index_offset + labels_dense.ravel()] = 1
  return labels_one_hot

def extract_labels(filename, one_hot=False):
  """Extract the labels into a 1D uint8 numpy array [index]."""
  print('Extracting', filename)
  with gzip.open(filename) as bytestream:
    num_items = _read32(bytestream)
    # num_items = 80000
    buf = bytestream.read(num_items*2)
    dt = numpy.dtype(numpy.uint16).newbyteorder('>')
    labels = numpy.frombuffer(buf, dtype=dt)

    if one_hot:
      return dense_to_one_hot(labels, 361)
    return labels

# def extract_labels(filename, one_hot=False):
#   """Extract the labels into a 1D uint8 numpy array [index]."""
#   print('Extracting', filename)
#   with gzip.open(filename) as bytestream:
#     num_items = _read32(bytestream)
#     # num_items = 80000
#     buf = bytestream.read(num_items)
#     labels = numpy.frombuffer(buf, dtype=numpy.uint8)
#     if one_hot:
#       return dense_to_one_hot(labels)
#     return labels

class DataSet(object):
  def __init__(self, images, labels, fake_data=False, one_hot=False):
    """Construct a DataSet. one_hot arg is used only if fake_data is true."""
    if fake_data:
      self._num_examples = 10000
      self.one_hot = one_hot
    else:
      assert images.shape[0] == labels.shape[0], (
          'images.shape: %s labels.shape: %s' % (images.shape,
                                                 labels.shape))
      self._num_examples = images.shape[0]
      # Convert shape from [num examples, rows, columns, depth]
      # to [num examples, rows*columns] (assuming depth == 1)
      # assert images.shape[3] == 3
      # images = images.reshape(images.shape[0],
      #                         images.shape[1] * images.shape[2])
      # Convert from [0, 255] -> [0.0, 1.0].
      images = images.astype(numpy.float32)
      # images = numpy.multiply(images, 1.0 / 255.0)
    self._images = images
    self._labels = labels
    self._epochs_completed = 0
    self._index_in_epoch = 0
  @property
  def images(self):
    return self._images
  @property
  def labels(self):
    return self._labels
  @property
  def num_examples(self):
    return self._num_examples
  @property
  def epochs_completed(self):
    return self._epochs_completed
  def next_batch(self, batch_size, fake_data=False):
    """Return the next `batch_size` examples from this data set."""
    if fake_data:
      fake_image = [1] * 784
      if self.one_hot:
        fake_label = [1] + [0] * 9
      else:
        fake_label = 0
      return [fake_image for _ in xrange(batch_size)], [
          fake_label for _ in xrange(batch_size)]
    start = self._index_in_epoch
    self._index_in_epoch += batch_size
    if self._index_in_epoch > self._num_examples:
      # Finished epoch
      self._epochs_completed += 1
      # Shuffle the data
      perm = numpy.arange(self._num_examples)
      numpy.random.shuffle(perm)
      self._images = self._images[perm]
      self._labels = self._labels[perm]
      # Start next epoch
      start = 0
      self._index_in_epoch = batch_size
      assert batch_size <= self._num_examples
    end = self._index_in_epoch
    return self._images[start:end], self._labels[start:end]


def read_data_sets(train_dir, fake_data=False, one_hot=False):
  class DataSets(object):
    pass
  data_sets = DataSets()
  if fake_data:
    data_sets.train = DataSet([], [], fake_data=True, one_hot=one_hot)
    data_sets.validation = DataSet([], [], fake_data=True, one_hot=one_hot)
    data_sets.test = DataSet([], [], fake_data=True, one_hot=one_hot)
    return data_sets
  GAMES = 'games.dat.gz'
  RESULTS = 'labels.dat.gz'
  VALIDATION_SIZE = 5000
  TEST_SIZE = 5000

  train_images = extract_images(os.path.join(train_dir, GAMES))
  train_labels = extract_labels(os.path.join(train_dir, RESULTS), one_hot=one_hot)

  # validation_images = train_images[:VALIDATION_SIZE]
  # validation_labels = train_labels[:VALIDATION_SIZE]
  # train_images = train_images[VALIDATION_SIZE:]
  # train_labels = train_labels[VALIDATION_SIZE:]

  test_images = train_images[-TEST_SIZE:]
  test_labels = train_labels[-TEST_SIZE:]
  train_images = train_images[:-TEST_SIZE]
  train_labels = train_labels[:-TEST_SIZE]

  data_sets.train = DataSet(train_images, train_labels)
  # data_sets.validation = DataSet(validation_images, validation_labels)
  data_sets.test = DataSet(test_images, test_labels)
  return data_sets