import input_data
import tensorflow as tf

def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')


eren_go = input_data.read_data_sets("data/", one_hot=True)


b = tf.Variable(tf.zeros([10]))
y_ = tf.placeholder(tf.float32, [None, 10])



W_conv1 = weight_variable([5, 5, 2, 32])
b_conv1 = bias_variable([32])

# x_image = tf.reshape(x, [-1,28,28,1])
x_image = tf.placeholder(tf.float32, [None, 19, 19, 2])

# h_conv1 = tf.nn.relu(tf.nn.conv2d(x_image, W_conv1, strides=[1, 1, 1, 1], padding='VALID') + b_conv1)
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

W_conv2 = weight_variable([5, 5, 32, 64])
b_conv2 = bias_variable([64])

h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

W_fc1 = weight_variable([5 * 5 * 64, 1024])
b_fc1 = bias_variable([1024])

h_pool2_flat = tf.reshape(h_pool2, [-1, 5*5*64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

keep_prob = tf.placeholder("float")
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)


W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])

y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

cross_entropy = -tf.reduce_sum(y_*tf.log(y_conv))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

init = tf.initialize_all_variables()
sess = tf.Session()
# sess.run(init)
sess.run(tf.initialize_all_variables())

for i in range(40000):
  batch = eren_go.train.next_batch(50)
  if i%100 == 0:
    train_accuracy = sess.run(accuracy,feed_dict={
        x_image:batch[0], y_: batch[1], keep_prob: 1.0})
    print "step %d, training accuracy %g"%(i, train_accuracy)
  if i%1000 == 0:
    print "test accuracy %g"%sess.run(accuracy, feed_dict={
        x_image: eren_go.test.images, y_: eren_go.test.labels, keep_prob: 1.0})
  sess.run(train_step, feed_dict={x_image: batch[0], y_: batch[1], keep_prob: 0.5})


print "test accuracy %g"%sess.run(accuracy, feed_dict={
    x_image: eren_go.test.images, y_: eren_go.test.labels, keep_prob: 1.0})