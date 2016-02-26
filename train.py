from load_data import read_data_sets
import tensorflow as tf
import os.path
import argparse

parser = argparse.ArgumentParser(description='Train a DCNN to learn how to play Go.')

parser.add_argument('--output-dir', default='data/models/32_layers/', help='Data directory (default: data/models/32_layers/)', dest='output_dir')
parser.add_argument('--data-file', default='data/training/32_layers.hdf5', help='Data file (default: data/training/32_layers.hdf5)', dest='data_file')
parser.add_argument('--num-steps', default=300000, type=int, help='Number of steps of execution (default: 300000)', dest='num_steps')
parser.add_argument('--batch-size', default=16, type=int, help='Batch size (default: 16)', dest='batch_size')
parser.add_argument('--layer-count', default=12, type=int, help='Number of convolutions layers  (default: 12)', dest='layer_count')
parser.add_argument('--filter-count', default=192, type=int, help='Number of convolutions filters  (default: 192)', dest='filter_count')
parser.add_argument('--dropout', type=float, help='Dropout (if none is given, no dropout)', dest='dropout')

args = parser.parse_args()

def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding="SAME")

data_set = read_data_sets(args.data_file)

print("Training Position Shape: {}".format(data_set.train.positions.shape))
print("Training Label Shape: {}".format(data_set.train.labels.shape))
print("Test Position Shape: {}".format(data_set.test.positions.shape))
print("Test Label Shape: {}".format(data_set.test.labels.shape))

num_input_layers = data_set.train.num_layers

b = tf.Variable(tf.zeros([361]))
y_ = tf.placeholder(tf.float32, [None, 361])

x_image = tf.placeholder(tf.float32, [None, 19, 19, num_input_layers])

W_conv = weight_variable([5, 5, num_input_layers, args.filter_count])
b_conv = bias_variable([args.filter_count])
last_h_conv = tf.nn.relu(conv2d(x_image, W_conv) + b_conv)

for i in range(args.layer_count - 2):
  W_conv = weight_variable([3, 3, args.filter_count, args.filter_count])
  b_conv = bias_variable([args.filter_count])
  h_conv = tf.nn.relu(conv2d(last_h_conv, W_conv) + b_conv)

  last_h_conv = h_conv

W_conv = weight_variable([1, 1, args.filter_count, 1])
b_conv = bias_variable([361])
softmax_input = tf.reshape(conv2d(last_h_conv, W_conv), [-1, 361]) + b_conv

keep_prob = tf.placeholder("float")

# if args.dropout:
#   softmax_input_drop = tf.nn.dropout(softmax_input, keep_prob)
# else:
#   softmax_input_drop = softmax_input

y_conv = tf.nn.softmax(softmax_input)

cross_entropy = -tf.reduce_sum(y_*tf.log(tf.clip_by_value(y_conv,1e-10,1.0)))
train_step = tf.train.AdamOptimizer(learning_rate=1e-4, beta1=0.9, beta2=0.999, epsilon=1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

saver = tf.train.Saver()

sess = tf.Session()
sess.run(tf.initialize_all_variables())

# if os.path.isfile(args.output_dir + "model.ckpt"):
#   saver.restore(sess, args.output_dir + "model.ckpt")
#   print("Model restored.")

for i in range(args.num_steps):
  batch = data_set.train.next_batch(args.batch_size)
  if i%10000 == 0:
    print "epoch: %g"%data_set.train.epoch()
    print "test accuracy %g"%sess.run(accuracy, feed_dict={
      x_image: data_set.test.all_positions(), y_: data_set.test.all_labels(), keep_prob: 1.0})
    save_path = saver.save(sess, args.output_dir + "model_" + str(i) + ".ckpt")
    print("Model saved in file: ", save_path)

  if i%500 == 0:
    train_accuracy = sess.run(accuracy,feed_dict={
      x_image:batch[0], y_: batch[1], keep_prob: 1.0})
    print "step %d, training accuracy %g"%(i, train_accuracy)

  sess.run(train_step, feed_dict={x_image: batch[0], y_: batch[1], keep_prob: args.dropout})

print "test accuracy %g"%sess.run(accuracy, feed_dict={
  x_image: data_set.test.all_positions(), y_: data_set.test.all_labels(), keep_prob: 1.0})
save_path = saver.save(sess, args.output_dir + "model.ckpt")
print("Model saved in file: ", save_path)
