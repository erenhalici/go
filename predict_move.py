
import numpy as np
import tensorflow as tf
import os.path

def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding="VALID")

num_input_layers = 8
filter_depths = [32, 48, 64, 96]
fc_size = 512

b = tf.Variable(tf.zeros([361]))

x_image = tf.placeholder(tf.float32, [1, 19, 19, num_input_layers])
legal = tf.placeholder(tf.float32, [1, 19, 19])

last_depth = filter_depths.pop(0)

W_conv = weight_variable([5, 5, num_input_layers, last_depth])
b_conv = bias_variable([last_depth])
last_h_conv = tf.nn.relu(conv2d(x_image, W_conv) + b_conv)

size = 15

while filter_depths:
  depth = filter_depths.pop(0)

  W_conv = weight_variable([3, 3, last_depth, depth])
  b_conv = bias_variable([depth])
  h_conv = tf.nn.relu(conv2d(last_h_conv, W_conv) + b_conv)

  last_depth = depth
  last_h_conv = h_conv

  size -= 2

conv_output = tf.reshape(last_h_conv, [-1, size * size * last_depth])

if fc_size:
  W_fc = weight_variable([size * size * last_depth, fc_size])
  b_fc = bias_variable([fc_size])
  softmax_input = tf.nn.relu(tf.matmul(conv_output, W_fc) + b_fc)
  softmax_input_size = fc_size
else:
  softmax_input = conv_output
  softmax_input_size = size * size * last_depth

W_softmax = weight_variable([softmax_input_size, 361])
b_softmax = bias_variable([361])

y_conv = tf.nn.softmax(tf.matmul(softmax_input, W_softmax) + b_softmax)
filtered = tf.mul(tf.reshape(legal, [-1, 361]), y_conv)

next_move = tf.argmax(filtered, 1)

next_moves = tf.nn.top_k(filtered, 1)

saver = tf.train.Saver()

sess1 = tf.Session()
sess1.run(tf.initialize_all_variables())
saver.restore(sess1, "model_593000_0219.ckpt")

sess2 = tf.Session()
sess2.run(tf.initialize_all_variables())
saver.restore(sess2, "model_93000_00874.ckpt")
# saver.restore(sess2, "model_159000_01715.ckpt")
# saver.restore(sess2, "model_446000_02135.ckpt")

def predict_move(board, legal_moves, second_model):
  if second_model:
    predictions = sess1.run(next_moves, feed_dict={x_image: [board], legal: [legal_moves]})
  else:
    predictions = sess2.run(next_moves, feed_dict={x_image: [board], legal: [legal_moves]})

  # print predictions

  probs = predictions[0][0].tolist()
  moves = predictions[1][0].tolist()

  prob = np.random.rand()
  prob = prob * sum(probs)

  # print prob

  cumulative = 0

  while cumulative < prob:
    move = moves.pop(0)
    cumulative += probs.pop(0)

  return (int(move/19), move%19)

  # if second_model:
  #   move = sess1.run(next_move, feed_dict={x_image: [board], legal: [legal_moves]})
  # else:
  #   move = sess2.run(next_move, feed_dict={x_image: [board], legal: [legal_moves]})
  # return (int(move[0]/19), move[0]%19)
