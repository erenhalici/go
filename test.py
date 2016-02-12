import numpy as np
import h5py

def load():
  f = h5py.File("data/training/32_layers.hdf5", 'r')
  positions = f['positions']
  labels = f['labels']
  return (positions, labels)

def position(positions, index):
  layers = positions.attrs['layers']
  return np.unpackbits(positions[index])[:19*19*layers].reshape(19,19,layers).transpose(2,0,1)

def label(labels, index):
  classes = labels.attrs['classes']
  return np.unpackbits(labels[index])[:classes-1].reshape(19,19)
