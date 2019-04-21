import tensorflow as tf
import numpy as np
import os
import argparse
import pickle
import random
import threading
import time

INPUT_DATA = 32 * 32
OUTPUT_NODE = 10

IMAGE_SIZE = 32
NUM_CHANNELS = 3
NUM_LABELS = 10

# level 1
CONV1_SIZE = 5
CONV1_DEEP = 32

# pool
POOL1_SIZE = 3
# POOL2_DEEP = N/A

# level 2
CONV2_SIZE = 5
CONV2_DEEP = 64

# full connect

# level 3
FC1_SIZE = 128

# level 4
FC2_SIZE = 192

# level 5
NUM_CLASSES = NUM_LABELS

BATCH_SIZE = 100
EPOCH_SIZE = 1
NUM_BATCHES_PER_EPOCH = 500
NUM_EPOCHS_PER_DECAY = 6


LEARNING_RATE_INITIAL = 0.1
LEARNING_RATE_DECAY = 0.1
REGULARIZATION_RATE = 0.004
MOVING_AVERAGE_DECAY = 0.99

DATA_PATH = 'cifar-10-batches-py/data_batch_'
MODEL_SAVE_DIR_NAME = 'model/'
MODEL_SAVE_FILE_NAME = 'model/cifar10.model'
# gdrive/My Drive/GPU/
def infer(images, train, regularizer = None):
    with tf.variable_scope('conv1') as scope:
        conv1_weight = tf.get_variable(
            'weight',
            [CONV1_SIZE, CONV1_SIZE, NUM_CHANNELS, CONV1_DEEP],
            initializer = tf.truncated_normal_initializer(stddev = 0.1)
        )
        conv1_bias = tf.get_variable(
            'bias',
            [CONV1_DEEP],
            initializer = tf.constant_initializer(0.0)
        )
        conv1 = tf.nn.conv2d(
            images,
            conv1_weight,
            strides = [1, 1, 1, 1],
            padding = 'SAME'
        )
        conv1 = tf.nn.bias_add(
            conv1,
            conv1_bias
        )
        conv1 = tf.nn.relu(conv1)
    pool1 = tf.nn.max_pool(
        conv1,
        ksize = [1, 3, 3, 1],
        strides = [1, 2, 2, 1],
        padding = 'SAME'
    )
    norm1 = tf.nn.lrn(pool1, depth_radius = 4, bias = 1.0, alpha = 0.001 / 9.0, beta = 0.75)

    with tf.variable_scope('conv2'):
        conv2_weight = tf.get_variable(
            'weight',
            [CONV2_SIZE, CONV2_SIZE, CONV1_DEEP, CONV2_DEEP],
            initializer = tf.truncated_normal_initializer(stddev = 0.1)
        )
        conv2_bias = tf.get_variable(
            'bias',
            [CONV2_DEEP],
            initializer = tf.constant_initializer(0.1)
        )
        conv2 = tf.nn.conv2d(
            conv1,
            conv2_weight,
            strides = [1, 1, 1, 1],
            padding = 'SAME'
        )
        conv2 = tf.nn.bias_add(
            conv2,
            conv2_bias
        )
        conv2 = tf.nn.relu(conv2)
    norm2 = tf.nn.lrn(conv2, depth_radius = 4, bias = 1.0, alpha = 0.001 / 9.0, beta = 0.75)
    pool2 = tf.nn.max_pool(
        norm2,
        ksize = [1, 3, 3, 1],
        strides = [1, 2, 2, 1],
        padding = 'SAME'        
    )

    # dropout
    pool2 = tf.nn.dropout(pool2, keep_prob = 0.5)

    with tf.variable_scope('fc1'):
        reshape = tf.reshape(pool2, [BATCH_SIZE, -1])
        dimension = reshape.get_shape()[1].value
        fc1_weight = tf.get_variable(
            'weight',
            [dimension, FC1_SIZE],
            initializer = tf.truncated_normal_initializer(stddev = 0.1)
        )
        # regular item
        if regularizer is not None:
            tf.add_to_collection('losses', regularizer(fc1_weight))
        fc1_bias = tf.get_variable(
            'bias',
            [FC1_SIZE],
            initializer = tf.constant_initializer(0.1)
        )
        fc1 = tf.matmul(
            reshape,
            fc1_weight
        ) + fc1_bias
        fc1 = tf.nn.relu(fc1)

    with tf.variable_scope('fc2'):
        fc2_weight = tf.get_variable(
            'weight',
            [FC1_SIZE, FC2_SIZE],
            initializer = tf.truncated_normal_initializer(stddev = 0.1)
        )
        # regular item
        if regularizer is not None:
            tf.add_to_collection('losses', regularizer(fc2_weight))
        fc2_bias = tf.get_variable(
            'bias',
            [FC2_SIZE],
            initializer = tf.constant_initializer(0.1)
        )
        fc2 = tf.matmul(
            fc1,
            fc2_weight
        ) + fc2_bias
        fc2 = tf.nn.relu(fc2)
  
    # linear layer
    with tf.variable_scope('fc3'):
        fc3_weight = tf.get_variable(
            'weight',
            [FC2_SIZE, NUM_CLASSES],
            initializer = tf.truncated_normal_initializer(stddev = 0.1)
        )
        # regular item
        if regularizer is not None:
            tf.add_to_collection('losses', regularizer(fc3_weight))
        fc3_bias = tf.get_variable(
            'bias',
            [NUM_CLASSES],
            initializer = tf.constant_initializer(0.1)
        )
        fc3 = tf.matmul(
            fc2,
            fc3_weight
        ) + fc3_bias
        fc3 = tf.nn.relu(fc3)
    # shape == (BACH_SIZE, NUM_CLASSES)
    return fc2

def loss(logits, labels):
    labels = tf.cast(labels, tf.int64)
    # labels [BATCH_SIZE]
    # logits [BATCH_SIZE, NUM_CLASSES]
    cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
        labels = labels,
        logits = logits
    )
    cross_entropy_mean = tf.reduce_mean(cross_entropy)

    return cross_entropy_mean + tf.add_n(tf.get_collection('losses'))

def train(loss, global_step):
    steps_per_decay = int(NUM_BATCHES_PER_EPOCH * NUM_EPOCHS_PER_DECAY)
    lr = tf.train.exponential_decay(
        LEARNING_RATE_INITIAL,
        global_step,
        steps_per_decay,
        LEARNING_RATE_DECAY,
        staircase = True
    )
    train_op = tf.train.GradientDescentOptimizer(lr).minimize(loss, global_step = global_step)
    variable_average = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY, global_step)
    variable_average_op = variable_average.apply(tf.trainable_variables())
    with tf.control_dependencies([ train_op, variable_average_op ]):
        final_op = tf.no_op('final_op')
    
    return final_op

def next_batch(batch_id = 0):
    #real_id = batch_id % 5 + 1
    #file_name = DATA_PATH + str(real_id)
    #with open(file_name, 'rb') as f:
    #    d = pickle.load(f, encoding = 'latin1')
    #all_data = d['data'].reshape(10000, NUM_CHANNELS, IMAGE_SIZE, IMAGE_SIZE).transpose(0, 2, 3, 1)
    #all_labels = d['labels']
    global all_data
    global all_labels
    target_data_index = np.random.choice(all_data.shape[0], BATCH_SIZE, replace = False)
    return all_data[target_data_index, :], [all_labels[i] for i in target_data_index]

def main_train():
    x = tf.placeholder(
        tf.float32,
        [BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS],
        name = 'x-input'
    )
    y_ = tf.placeholder(
        tf.float32,
        [BATCH_SIZE],
        name = 'y-input'
    )

    regularizer = tf.contrib.layers.l2_regularizer(REGULARIZATION_RATE)
    y = infer(x, True, regularizer)
    losses = loss(y, y_)
    global_step = tf.Variable(0, trainable = False)
    final_op = train(losses, global_step)

    total_training_step = NUM_BATCHES_PER_EPOCH * EPOCH_SIZE
    saver = tf.train.Saver()
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        for i in range(total_training_step):
            xf, y_f = next_batch(i)
            _, cur_loss, step = sess.run([final_op, losses, global_step], feed_dict = {
                x: xf,
                y_: y_f
            })
            print('After {} batches, loss on trainning batch is {:.4f}'.format(i, cur_loss))                    
            if not (i + 1) % 10:
                saver.save(sess, MODEL_SAVE_FILE_NAME, global_step = global_step)

def get_test_data():
    #with open('cifar-10-batches-py/test_batch', 'rb') as f:
    #    d = pickle.load(f, encoding = 'latin1')
    #all_data = d['data'].reshape(10000, NUM_CHANNELS, IMAGE_SIZE, IMAGE_SIZE).transpose(0, 2, 3, 1)
    #all_labels = d['labels']
    global all_data
    global all_labels
    target_data_index = np.random.choice(all_data.shape[0], BATCH_SIZE, replace = False)
    return all_data[target_data_index, :], [all_labels[i] for i in target_data_index]    

def main_evaluate():
    with tf.Graph().as_default() as g:
        x = tf.placeholder(
            tf.float32,
            [BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS],
            name = 'x-input'
        )
        y_ = tf.placeholder(
            tf.int64,
            [BATCH_SIZE],
            name = 'y-input'
        )
        y = infer(x, False)
        correct_predict = tf.equal(y_, tf.argmax(y, axis = 1))
        accuracy = tf.reduce_mean(tf.cast(correct_predict, tf.float32))

        ema = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY)
        variables_to_restore = ema.variables_to_restore()
        saver = tf.train.Saver(variables_to_restore)
        total_training_step = NUM_BATCHES_PER_EPOCH * EPOCH_SIZE
        while True:
            with tf.Session(graph = g) as sess:
                model = tf.train.get_checkpoint_state(MODEL_SAVE_DIR_NAME)
                if model and model.model_checkpoint_path:
                    saver.restore(sess, model.model_checkpoint_path)
                    global_step = model.model_checkpoint_path.split('/')[-1].split('-')[-1]
                    xf, y_f = get_test_data()
                    accuracy_value = sess.run(accuracy, feed_dict = {
                        x: xf,
                        y_: y_f
                    })
                    print(model.model_checkpoint_path)
                    print('After {} training steps, accuracy is {:.4f}'.format(global_step, accuracy_value))
                    if int(global_step) == total_training_step:
                        break;
                else:
                    print('No checkpoint yet')
            time.sleep(10)
def generate_csv():
    with tf.Graph().as_default() as g:
        image = np.load('../input/test_images.npy')
        data = image.transpose(0, 2, 3, 1)
        data = np.array(data, dtype = float) / 255.0
        ret = np.zeros([ data.shape[0] ], dtype = 'int64')
        x = tf.placeholder(
            tf.float32,
            [BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS],
            name = 'x-input'
        )
        y = infer(x, False)
        eval_result = tf.argmax(y, axis = 1)
        ema = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY)
        variables_to_restore = ema.variables_to_restore()
        saver = tf.train.Saver(variables_to_restore)
        num_of_times = data.shape[0] // BATCH_SIZE
        with tf.Session(graph = g) as sess:
            model = tf.train.get_checkpoint_state(MODEL_SAVE_DIR_NAME)
            if model and model.model_checkpoint_path:
                saver.restore(sess, model.model_checkpoint_path)
                for i in range(num_of_times):
                    xf = data[i * BATCH_SIZE:(i + 1) * BATCH_SIZE, :]
                    eval_result_ret = sess.run(eval_result, feed_dict = {
                        x: xf
                    })
                    ret[i * BATCH_SIZE:(i + 1) * BATCH_SIZE] = np.array(map(lambda x: typeList[x], eval_result_ret))
    data_to_submit = pd.DataFrame({
        'Id': range(1, data.shape[0] + 1),
        'Category': ret
    })
    data_to_submit.to_csv('submission.csv', index = False)

typeList = [ 'frog', 'truck', 'automobile', 'bird', 'horse', 'ship', 'cat', 'dog', 'airplane', 'deer' ]
typeDict = dict(zip(typeList, range(len(typeList))))
file_name = '../input/train_images.npy'
d = np.load(file_name)
all_data = d.transpose(0, 2, 3, 1)
all_data = np.array(all_data, dtype = float) / 255.0
# all_data = all_data / 255.0
# all_labels = np.genfromtxt('../input/train_labels.csv', delimiter = ',')
l = [ ]
with open('../input/train_labels.csv', 'r') as f:
    import csv
    spam = csv.reader(f)
    for line in spam:
        l.append(line[1] if len(line) == 2 else line)
l.remove(l[0])
v = np.vectorize(lambda x: typeDict[x])
all_labels = list(map(lambda x: typeDict[x], l))

if __name__ == '__main__':
    eval_thread = threading.Thread(target = main_evaluate)
    eval_thread.start()
    main_train()
    eval_thread.join()
    generate_csv()