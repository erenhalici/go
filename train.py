import input_data
import tensorflow as tf
import os.path
import argparse

parser = argparse.ArgumentParser(description='Train a DCNN to learn how to play Go.')

parser.add_argument('--data-dir', help='Data directory (default: data/moves_single)', dest='data_dir')
parser.add_argument('--num-layers', default=8, type=int, help='Number of input layers (default: 8)', dest='num_input_layers')
parser.add_argument('--num-steps', default=300000, type=int, help='Number of steps of execution (default: 300000)', dest='num_steps')
parser.add_argument('--filter-depths', nargs='+', default=[32, 64, 96], type=int, help='Depths of the convolutions layers  (default: [32, 64, 96])', dest='filter_depths')
parser.add_argument('--fc-size', type=int, help='Number neurons in the fully connected layer (if none is given, no fully connected layer)', dest='fc_size')
parser.add_argument('--dropout', type=float, help='Dropout (if none is given, no dropout)', dest='dropout')

args = parser.parse_args()

print args.filter_depths
print args.fc_size

def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding="VALID")


data_set = input_data.read_data_sets(args.data_dir, args.num_input_layers)

b = tf.Variable(tf.zeros([361]))
y_ = tf.placeholder(tf.float32, [None, 361])

x_image = tf.placeholder(tf.float32, [None, 19, 19, args.num_input_layers])

last_depth = args.filter_depths.pop(0)

W_conv = weight_variable([5, 5, args.num_input_layers, last_depth])
b_conv = bias_variable([last_depth])
last_h_conv = tf.nn.relu(conv2d(x_image, W_conv) + b_conv)

size = 15

while args.filter_depths:
  depth = args.filter_depths.pop(0)

  W_conv = weight_variable([3, 3, last_depth, depth])
  b_conv = bias_variable([depth])
  h_conv = tf.nn.relu(conv2d(last_h_conv, W_conv) + b_conv)

  last_depth = depth
  last_h_conv = h_conv

  size -= 2

conv_output = tf.reshape(last_h_conv, [-1, size * size * last_depth])
keep_prob = tf.placeholder("float")

if args.fc_size:
  W_fc = weight_variable([size * size * last_depth, args.fc_size])
  b_fc = bias_variable([args.fc_size])
  softmax_input = tf.nn.relu(tf.matmul(conv_output, W_fc) + b_fc)
  softmax_input_size = args.fc_size
else:
  softmax_input = conv_output
  softmax_input_size = size * size * last_depth

if args.dropout:
  softmax_input_drop = tf.nn.dropout(softmax_input, keep_prob)
else:
  softmax_input_drop = softmax_input

W_softmax = weight_variable([softmax_input_size, 361])
b_softmax = bias_variable([361])

y_conv = tf.nn.softmax(tf.matmul(softmax_input_drop, W_softmax) + b_softmax)

print size
print softmax_input_size

cross_entropy = -tf.reduce_sum(y_*tf.log(tf.clip_by_value(y_conv,1e-10,1.0)))
train_step = tf.train.AdamOptimizer(learning_rate=1e-4, beta1=0.9, beta2=0.999, epsilon=1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

saver = tf.train.Saver()

sess = tf.Session()
sess.run(tf.initialize_all_variables())

# if os.path.isfile(args.data_dir + "model.ckpt"):
#   saver.restore(sess, args.data_dir + "model.ckpt")
#   print("Model restored.")

for i in range(args.num_steps):
  batch = data_set.train.next_batch(128)
  if i%1000 == 0:
    print("epoch: {}".format(data_set.train.epochs_completed))
    print "test accuracy %g"%sess.run(accuracy, feed_dict={
        x_image: data_set.test.images, y_: data_set.test.labels, keep_prob: 1.0})
    save_path = saver.save(sess, args.data_dir + "model_" + str(i) + ".ckpt")
    print("Model saved in file: ", save_path)

  if i%100 == 0:
    train_accuracy = sess.run(accuracy,feed_dict={
        x_image:batch[0], y_: batch[1], keep_prob: 1.0})
    print "step %d, training accuracy %g"%(i, train_accuracy)

  sess.run(train_step, feed_dict={x_image: batch[0], y_: batch[1], keep_prob: args.dropout})

print "test accuracy %g"%sess.run(accuracy, feed_dict={
    x_image: data_set.test.images, y_: data_set.test.labels, keep_prob: 1.0})
save_path = saver.save(sess, args.data_dir + "model.ckpt")
print("Model saved in file: ", save_path)
