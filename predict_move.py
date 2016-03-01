
import numpy as np
import tensorflow as tf
import os.path

from model import *

min_prob = 1

with tf.Graph().as_default():
  model = Model(32, 6, 64)

  saver = tf.train.Saver()
  sess1 = tf.Session()
  sess1.run(tf.initialize_all_variables())
  saver.restore(sess1, "data/models/6_64/model.ckpt")

with tf.Graph().as_default():
  model = Model(32, 8, 96)

  saver = tf.train.Saver()
  sess2 = tf.Session()
  sess2.run(tf.initialize_all_variables())
  saver.restore(sess2, "data/models/8_96/model_320000_02894.ckpt")

def predict_move(board, legal_moves, second_model):
  global min_prob

  if second_model:
    predictions = sess1.run(model.next_moves, feed_dict={model.x_image: [board], model.legal: [legal_moves]})
  else:
    predictions = sess2.run(model.next_moves, feed_dict={model.x_image: [board], model.legal: [legal_moves]})

  # print predictions

  probs = predictions[0][0].tolist()
  moves = predictions[1][0].tolist()

  prob = np.random.rand()
  prob = prob * sum(probs)

  cumulative = 0

  if probs[0] < 0.01:
    return (-1, -1)

  if probs[0] < min_prob:
    min_prob = probs[0]
    print(min_prob)

  while cumulative < prob:
    move = moves.pop(0)
    cumulative += probs.pop(0)

  return (int(move/19), move%19)
