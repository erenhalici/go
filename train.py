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
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding="VALID")

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding="SAME")

DATA_DIR = "data/moves_single/"
NUM_INPUT_LAYERS = 8
NUM_STEPS = 300000

data_set = input_data.read_data_sets(DATA_DIR, NUM_INPUT_LAYERS)

b = tf.Variable(tf.zeros([361]))
y_ = tf.placeholder(tf.float32, [None, 361])

x_image = tf.placeholder(tf.float32, [None, 19, 19, NUM_INPUT_LAYERS])

W_conv1 = weight_variable([5, 5, NUM_INPUT_LAYERS, 32])
b_conv1 = bias_variable([32])
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)

W_conv2 = weight_variable([3, 3, 32, 64])
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(conv2d(h_conv1, W_conv2) + b_conv2)

W_conv3 = weight_variable([3, 3, 64, 96])
b_conv3 = bias_variable([96])
h_conv3 = tf.nn.relu(conv2d(h_conv2, W_conv3) + b_conv3)

W_fc1 = weight_variable([11 * 11 * 96, 1024])
b_fc1 = bias_variable([1024])
fc_input = tf.reshape(h_conv3, [-1, 11 * 11 * 96])

h_fc1 = tf.nn.relu(tf.matmul(fc_input, W_fc1) + b_fc1)

keep_prob = tf.placeholder("float")
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

W_fc2 = weight_variable([1024, 361])
b_fc2 = bias_variable([361])

y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

cross_entropy = -tf.reduce_sum(y_*tf.log(tf.clip_by_value(y_conv,1e-10,1.0)))
train_step = tf.train.AdamOptimizer(learning_rate=1e-4, beta1=0.9, beta2=0.999, epsilon=1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

saver = tf.train.Saver()

sess = tf.Session()
sess.run(tf.initialize_all_variables())

# if os.path.isfile(DATA_DIR + "model.ckpt"):
#   saver.restore(sess, DATA_DIR + "model.ckpt")
#   print("Model restored.")

for i in range(NUM_STEPS):
  batch = data_set.train.next_batch(128)
  if i%1000 == 0:
    print "test accuracy %g"%sess.run(accuracy, feed_dict={
        x_image: data_set.test.images, y_: data_set.test.labels, keep_prob: 1.0})
    save_path = saver.save(sess, DATA_DIR + "model_" + str(i) + ".ckpt")
    print("Model saved in file: ", save_path)

  if i%100 == 0:
    train_accuracy = sess.run(accuracy,feed_dict={
        x_image:batch[0], y_: batch[1], keep_prob: 1.0})
    print "step %d, training accuracy %g"%(i, train_accuracy)

  sess.run(train_step, feed_dict={x_image: batch[0], y_: batch[1], keep_prob: 0.5})

print "test accuracy %g"%sess.run(accuracy, feed_dict={
    x_image: data_set.test.images, y_: data_set.test.labels, keep_prob: 1.0})
save_path = saver.save(sess, DATA_DIR + "model.ckpt")
print("Model saved in file: ", save_path)
