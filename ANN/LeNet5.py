import tensorflow as tf
import tensorflow.examples.tutorials.mnist
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np
import os
import time
import argparse

INPUT_NODE = 28 * 28
OUTPUT_NODE = 10

IMAGE_SIZE = 28
NUM_CHANNELS = 1
NUM_LABELS = 10

# level 1
CONV1_DEEP = 32
CONV1_SIZE = 5

# level 2
CONV2_DEEP = 64
CONV2_SIZE = 5

# full connect level
FC_SIZE = 512


# train parameters
BATCH_SIZE = 100
LEARNING_RATE_BASE = 0.8
LEARNING_RATE_DECAY = 0.99
REGULARIZATION_RATE = 0.0001 # lambda
TRAINING_STEPS = 30000 # epoch * step
MOVING_AVERAGE_DECAY = 0.99

MODEL_SAVE_PATH = 'model/'
MODEL_SAVE_FILE_NAME = 'model/lenet5.model'

# construct this net
def infer(input_layer, train: bool, regularizer):
    with tf.variable_scope('layer1-conv'):
        conv1_weights = tf.get_variable(
            'weight',
            [CONV1_SIZE, CONV1_SIZE, NUM_CHANNELS, CONV1_DEEP],
            initializer = tf.truncated_normal_initializer(stddev = 0.1)
        )
        conv1_biases = tf.get_variable(
            'bias',
            [CONV1_DEEP],
            initializer = tf.constant_initializer(0.0)
        )
        conv1 = tf.nn.conv2d(
            input_layer,
            conv1_weights,
            strides = [1, 1, 1, 1],
            padding = 'SAME'
        )
        relu1 = tf.nn.relu(tf.nn.bias_add(conv1, conv1_biases))

    with tf.variable_scope('layer2-pool'):
        pool2 = tf.nn.max_pool(
            relu1,
            ksize = [1, 2, 2, 1],
            strides = [1, 2, 2, 1],
            padding = 'SAME'
        )

    with tf.variable_scope('layer3-conv'):
        conv3_weights = tf.get_variable(
            'weight',
            [CONV2_SIZE, CONV2_SIZE, CONV1_DEEP, CONV2_DEEP],
            initializer = tf.truncated_normal_initializer(stddev = 0.1)
        )

        conv3_biases = tf.get_variable(
            'bias',
            [CONV2_DEEP],
            initializer = tf.constant_initializer(0.0)
        )

        conv3 = tf.nn.conv2d(
            pool2,
            conv3_weights,
            strides = [1, 1, 1, 1],
            padding = 'SAME'
        )

        relu3 = tf.nn.relu(tf.nn.bias_add(conv3, conv3_biases))

    with tf.variable_scope('layer4-pool'):
        pool4 = tf.nn.max_pool(
            relu3,
            ksize = [1, 2, 2, 1],
            strides = [1, 2, 2, 1],
            padding = 'SAME'
        )
    # 7 X 7 @64
    # make a column vector
    pool4_shape = pool4.get_shape().as_list()
    pool4_neurons_num = pool4_shape[1] * pool4_shape[2] * pool4_shape[3];
    pool4_reshaped = tf.reshape(pool4, [pool4_shape[0], pool4_neurons_num])

    with tf.variable_scope('layer5-fc'):
        fc5_weights = tf.get_variable(
            'weight',
            [pool4_neurons_num, FC_SIZE],
            initializer = tf.truncated_normal_initializer(stddev = 0.1)
        )

        # fc => regularize
        if regularizer != None:
            tf.add_to_collection('losses', regularizer(fc5_weights))

        fc5_biases = tf.get_variable(
            'bias',
            [FC_SIZE],
            initializer = tf.constant_initializer(0.1)
        )

        fc5 = tf.matmul(pool4_reshaped, fc5_weights)
        relu5 = tf.nn.relu(fc5 + fc5_biases)

        if train:
            relu5 = tf.nn.dropout(relu5, keep_prob = 0.5)

        with tf.variable_scope('layer6-fc'):
            fc6_weights = tf.get_variable(
                'weight',
                [FC_SIZE, NUM_LABELS],
                initializer = tf.truncated_normal_initializer(stddev = 0.1)
            )
            if regularizer != None:
                tf.add_to_collection('losses', regularizer(fc6_weights))
            fc6_biases = tf.get_variable(
                'bias',
                [NUM_LABELS],
                initializer = tf.constant_initializer(0.1)
            )
            output = tf.matmul(relu5, fc6_weights) + fc6_biases

        return output


def train(*, mnist, dummy_arg = None):
    x = tf.placeholder(
        tf.float32,
        [BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS],
        name = 'x-input'
    )

    # label input
    y_ = tf.placeholder(
        tf.float32,
        # [None, NUM_LABELS],
        [BATCH_SIZE, NUM_LABELS],
        name = 'y-input'
    )

    regularizer = tf.contrib.layers.l2_regularizer(REGULARIZATION_RATE)
    # predict value
    y = infer(x, True, regularizer)
    global_step = tf.Variable(0, trainable = False)

    # ema(rate, nums_of_update)
    variable_averages = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY, global_step)
    variable_averages_op = variable_averages.apply(tf.trainable_variables())

    # maximum/maximal in row
    # maximum for single input example
    # sum for this batch
    cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels = tf.argmax(y_, 1), logits = y)

    # mean for this batch
    # loss function
    loss = tf.reduce_mean(cross_entropy) + tf.add_n(tf.get_collection('losses'))

    learning_rate = tf.train.exponential_decay(
        LEARNING_RATE_BASE,
        global_step,
        mnist.train.num_examples / BATCH_SIZE, # decay step
        LEARNING_RATE_DECAY
    )

    train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss, global_step = global_step)

    # group or
    # dependent variable
    # ema VS. training
    # tensors merge it
    with tf.control_dependencies([train_step, variable_averages_op]):
        train_op = tf.no_op('train') # how about name = 'train' ???

    saver = tf.train.Saver()
    with tf.Session() as sess:
        tf.initialize_all_variables().run()

        for i in range(TRAINING_STEPS):
            xs, ys = mnist.train.next_batch(BATCH_SIZE)
            xs = np.reshape(xs, [BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS])
            _, loss_value, step = sess.run([train_op, loss, global_step], feed_dict = {
                x: xs,
                y_: ys
            })

            if not i % 1000:
                print('After {} step(s), loss on training'
                      'batch is {}'.format(i, loss_value))
                saver.save(sess, MODEL_SAVE_FILE_NAME, global_step = global_step)


def main_train(argv = None):
    mnist = input_data.read_data_sets('MNIST_data/', one_hot = True)
    train(mnist = mnist, dummy_arg = { })


def evaluate(mnist):
    with tf.Graph().as_default() as g:
        x = tf.placeholder(
            tf.float32,
            [None, INPUT_NODE],
            name = 'x-input'
        )
        y_ = tf.placeholder(
            tf.float32,
            [None, OUTPUT_NODE],
            name = 'y-input'
        )

        # predict
        # just compute forward only once
        y = infer(x, False, None)
        correct_prediction = tf.equal(tf.argmax(y_, 1), tf.argmax(y, 1))

        # average in this batch/step
        # T/F -> float(1/0)
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        variable_averages = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY)
        variables_to_restore = variable_averages.variables_to_resore()
        saver = tf.train.Saver(variables_to_restore)
        while True:
            with tf.Session as sess:
                model = tf.train.get_checkpoint_state(MODEL_SAVE_PATH)
                if model and model.model_checkpoint_path:
                    saver.restore(sess, model.model_checkpoint_path)
                    global_step = model.model_checkpoint_path.split('/')[-1].split('-')[-1]
                    accuracy_value = sess.run(accuracy, feed_dict = {
                        x: mnist.validation.images,
                        y_: mnist.validation.labels
                    })
                    print('After {} training step(s), validation'
                          'accuracy = {}'.format(global_step, accuracy_value))
                else:
                    print('No checkpoint file found')
                    break
            # seconds integer
            time.sleep(10)
def main_evaluate(argv = None):
    mnist = input_data.read_data_sets('MNIST_data/', one_hot = True)
    evaluate(mnist)

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--validate',
                           required = False,
                           default = None,
                           help = 'just train it')
    args = argparser.parse_args()
    if args.validate is not None:
        main_train()
    else:
        main_evaluate()


if __name__ == '__main__':
    main()