from load_data import read_data_sets
import tensorflow as tf
import os.path
import argparse
from model import *

parser = argparse.ArgumentParser(description='Train a DCNN to learn how to play Go.')

parser.add_argument('--output-dir', default='data/models/32_layers/', help='Data directory (default: data/models/32_layers/)', dest='output_dir')
parser.add_argument('--data-file', default='data/training/32_layers.hdf5', help='Data file (default: data/training/32_layers.hdf5)', dest='data_file')
parser.add_argument('--num-steps', default=300000, type=int, help='Number of steps of execution (default: 300000)', dest='num_steps')
parser.add_argument('--batch-size', default=16, type=int, help='Batch size (default: 16)', dest='batch_size')
parser.add_argument('--layer-count', default=12, type=int, help='Number of convolutions layers  (default: 12)', dest='layer_count')
parser.add_argument('--filter-count', default=192, type=int, help='Number of convolutions filters  (default: 192)', dest='filter_count')
parser.add_argument('--dropout', type=float, help='Dropout (if none is given, no dropout)', dest='dropout')

args = parser.parse_args()

data_set = read_data_sets(args.data_file)

print("Training Position Shape: {}".format(data_set.train.positions.shape))
print("Training Label Shape: {}".format(data_set.train.labels.shape))
print("Test Position Shape: {}".format(data_set.test.positions.shape))
print("Test Label Shape: {}".format(data_set.test.labels.shape))

num_input_layers = data_set.train.num_layers

model = Model(num_input_layers, args.layer_count, args.filter_count)

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
    print "test accuracy %g"%sess.run(model.accuracy, feed_dict={
      x_image: data_set.test.all_positions(), y_: data_set.test.all_labels(), keep_prob: 1.0})
    save_path = saver.save(sess, args.output_dir + "model_" + str(i) + ".ckpt")
    print("Model saved in file: ", save_path)

  if i%500 == 0:
    train_accuracy = sess.run(model.accuracy,feed_dict={
      x_image:batch[0], y_: batch[1], keep_prob: 1.0})
    print "step %d, training accuracy %g"%(i, train_accuracy)

  sess.run(model.train_step, feed_dict={x_image: batch[0], y_: batch[1], keep_prob: args.dropout})

print "test accuracy %g"%sess.run(model.accuracy, feed_dict={
  x_image: data_set.test.all_positions(), y_: data_set.test.all_labels(), keep_prob: 1.0})
save_path = saver.save(sess, args.output_dir + "model.ckpt")
print("Model saved in file: ", save_path)
