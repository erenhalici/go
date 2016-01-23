import input_data
import tensorflow as tf
import os.path

def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding="SAME")

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding="SAME")


DATA_DIR = "data/winner_ko/"

eren_go = input_data.read_data_sets(DATA_DIR, one_hot=True)


b = tf.Variable(tf.zeros([2]))
y_ = tf.placeholder(tf.float32, [None, 2])

# W_conv1 = weight_variable([5, 5, 6, 32])
W_conv1 = weight_variable([5, 5, 7, 32])
b_conv1 = bias_variable([32])

# x_image = tf.placeholder(tf.float32, [None, 19, 19, 6])
x_image = tf.placeholder(tf.float32, [None, 19, 19, 7])

h_conv1 = tf.nn.relu(tf.nn.conv2d(x_image, W_conv1, strides=[1, 1, 1, 1], padding="VALID") + b_conv1)
# h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
# h_pool1 = max_pool_2x2(h_conv1)

# W_conv2 = weight_variable([3, 3, 32, 64])
# b_conv2 = bias_variable([64])

# h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
# h_pool2 = max_pool_2x2(h_conv2)

W_conv2 = weight_variable([3, 3, 32, 64])
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(tf.nn.conv2d(h_conv1, W_conv2, strides=[1, 1, 1, 1], padding="VALID") + b_conv2)

# W_conv3 = weight_variable([3, 3, 64, 96])
# b_conv3 = bias_variable([96])
# h_conv3 = tf.nn.relu(tf.nn.conv2d(h_conv2, W_conv3, strides=[1, 1, 1, 1], padding="VALID") + b_conv3)

W_fc1 = weight_variable([13 * 13 * 64, 1024])
b_fc1 = bias_variable([1024])

# fc_input = tf.reshape(h_pool2, [-1, 4 * 4 * 64])

fc_input = tf.reshape(h_conv2, [-1, 13 * 13 * 64])

h_fc1 = tf.nn.relu(tf.matmul(fc_input, W_fc1) + b_fc1)

keep_prob = tf.placeholder("float")
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

W_fc2 = weight_variable([1024, 2])
b_fc2 = bias_variable([2])

y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)


confidence = tf.placeholder("float")
y_confident = tf.greater(y_conv, confidence)
total_prediction = tf.reduce_sum(tf.cast(y_confident, "float"))
confident_prediction = tf.reduce_sum(tf.cast(tf.logical_and(y_confident, tf.equal(y_,1)),"float"))
# confident_accuracy = tf.div(tf.reduce_sum(tf.cast(confident_prediction, "float")), total_prediction)
confident_accuracy = tf.div(confident_prediction, total_prediction)

cross_entropy = -tf.reduce_sum(y_*tf.log(tf.clip_by_value(y_conv,1e-10,1.0)))
train_step = tf.train.AdamOptimizer(learning_rate=1e-4, beta1=0.9, beta2=0.999, epsilon=1e-4).minimize(cross_entropy)
# train_step = tf.train.AdagradOptimizer(learning_rate=1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

saver = tf.train.Saver()
# filter_summary = tf.image_summary("conv1", tf.split(3,32,W_conv1)[0])
w_hist = tf.histogram_summary("weights", W_conv1)

# init = tf.initialize_all_variables()
sess = tf.Session()
# sess.run(init)

merged = tf.merge_all_summaries()
# summary_writer = tf.train.SummaryWriter(DATA_DIR + "/logs", sess.graph_def)
summary_writer = tf.train.SummaryWriter(DATA_DIR + "/logs", sess.graph_def)

sess.run(tf.initialize_all_variables())

# if os.path.isfile(DATA_DIR + "model_200000.ckpt"):
#   saver.restore(sess, DATA_DIR + "model_200000.ckpt")
#   print("Model restored.")

writer = tf.train.SummaryWriter('logs')
filters = tf.transpose(W_conv1, [3, 0, 1, 2])

for i in range(6):
  summary_str = sess.run(tf.image_summary('Convolutional Layer ' + str(i), tf.split(3, 6, filters)[i], 32))
  writer.add_summary(summary_str)

writer.flush()
writer.close()


if os.path.isfile("data/winner_full/models/model_300000.ckpt"):
  saver.restore(sess, "data/winner_full/models/model_300000.ckpt")
  print("Model restored.")

for i in range(100000):
  batch = eren_go.train.next_batch(128)
  if i%1000 == 0:
    print "test accuracy %g"%sess.run(accuracy, feed_dict={
        x_image: eren_go.test.images, y_: eren_go.test.labels, keep_prob: 1.0})
    save_path = saver.save(sess, DATA_DIR + "model_" + str(i) + ".ckpt")
    print("Model saved in file: ", save_path)

  if i%100 == 0:
    train_accuracy = sess.run(accuracy,feed_dict={
        x_image:batch[0], y_: batch[1], keep_prob: 1.0})
    print "step %d, training accuracy %g"%(i, train_accuracy)

  sess.run(train_step, feed_dict={x_image: batch[0], y_: batch[1], keep_prob: 0.5})
  # sess.run(train_step, feed_dict={x_image: batch[0], y_: batch[1], keep_prob: 1.0})


print "test accuracy %g"%sess.run(accuracy, feed_dict={x_image: eren_go.test.images, y_: eren_go.test.labels, keep_prob: 1.0})




save_path = saver.save(sess, DATA_DIR + "model.ckpt")
print("Model saved in file: ", save_path)
# tf.run(filter_summary)
summary_str = sess.run(merged)
summary_writer.add_summary(summary_str, 0)
# summary_writer.add_summary(sess.run(filter_summary), 0)
summary_writer.add_graph(sess.graph_def)