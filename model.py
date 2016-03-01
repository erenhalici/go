
import tensorflow as tf

K = 1

class Model(object):
  def __init__(self, num_input_layers, layer_count, filter_count, learning_rate):
    b = tf.Variable(tf.zeros([361]))
    self._y_ = tf.placeholder(tf.float32, [None, 361])

    self._x_image = tf.placeholder(tf.float32, [None, 19, 19, num_input_layers])

    W_conv = self.weight_variable([5, 5, num_input_layers, filter_count])
    b_conv = self.bias_variable([filter_count])
    last_h_conv = tf.nn.relu(self.conv2d(self._x_image, W_conv) + b_conv)

    for i in range(layer_count - 2):
      W_conv = self.weight_variable([3, 3, filter_count, filter_count])
      b_conv = self.bias_variable([filter_count])
      h_conv = tf.nn.relu(self.conv2d(last_h_conv, W_conv) + b_conv)

      last_h_conv = h_conv

    W_conv = self.weight_variable([1, 1, filter_count, 1])
    b_conv = self.bias_variable([361])
    softmax_input = tf.reshape(self.conv2d(last_h_conv, W_conv), [-1, 361]) + b_conv

    self._keep_prob = tf.placeholder("float")

    # if dropout:
    #   softmax_input_drop = tf.nn.dropout(softmax_input, self._keep_prob)
    # else:
    #   softmax_input_drop = softmax_input

    y_conv = tf.nn.softmax(softmax_input)

    cross_entropy = -tf.reduce_sum(self._y_*tf.log(tf.clip_by_value(y_conv,1e-10,1.0)))
    self._train_step = tf.train.AdamOptimizer(learning_rate=learning_rate, beta1=0.9, beta2=0.999, epsilon=1e-4).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(self._y_,1))
    self._accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

    self._legal = tf.placeholder(tf.float32, [1, 19, 19])
    filtered = tf.mul(tf.reshape(self._legal, [-1, 361]), y_conv)
    self._next_move = tf.argmax(filtered, 1)
    self._next_moves = tf.nn.top_k(filtered, K)


  @property
  def x_image(self):
    return self._x_image
  @property
  def y_(self):
    return self._y_
  @property
  def keep_prob(self):
    return self._keep_prob
  @property
  def legal(self):
    return self._legal
  @property
  def train_step(self):
    return self._train_step
  @property
  def accuracy(self):
      return self._accuracy
  @property
  def next_move(self):
    return self._next_move
  @property
  def next_moves(self):
    return self._next_moves



  def weight_variable(self, shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

  def bias_variable(self, shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

  def conv2d(self, x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding="SAME")