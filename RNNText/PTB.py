from tensorflow.models.tutorials.rnn.ptb import reader
import tensorflow as tf
import numpy as np

DATA_DIR_NAME = './simple-examples/data/'
HIDDEN_SIZE = 200
NUM_LAYERS = 2
VOCAB_SIZE = 10000

LEARNING_RATE = 1.0
TRAIN_BATCH_SIZE = 20
TRAIN_NUM_STEPS = 35

EVAL_BATCH_SIZE = 1
EVAL_NUM_STEPS = 1
NUM_EPOCH = 2
KEEP_PROB = 0.5
MAX_GRAD_NORM = 5

TOTAL_STEPS = 1000

class PTBModel:
    def __init__(self, is_training, batch_size, num_steps):
        self.batch_size = batch_size
        self.num_steps = num_steps
        self.input_data = tf.placeholder(
            tf.int32,
            [batch_size, num_steps]
        )
        self.targets = tf.placeholder(
            tf.int32,
            [batch_size, num_steps]
        )
        lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(HIDDEN_SIZE)
        if is_training:
            lstm_cell = tf.nn.rnn_cell.DropoutWrapper(
                lstm_cell, output_keep_prob = KEEP_PROB
            )
        cell = tf.nn.rnn_cell.MultiRNNCell([lstm_cell] * NUM_LAYERS)
        self.initial_state = cell.zero_state(batch_size, tf.float32)
        embedding = tf.get_variable(
            'embedding',
            [VOCAB_SIZE, HIDDEN_SIZE]
        )
        # batch_size * num_steps
        # batch_size * num_steps * HIDDEN_SIZE
        # word => word vector
        inputs = tf.nn.embedding_lookup(embedding, self.input_data)
        if is_training:
            inputs = tf.nn.dropout(inputs, KEEP_PROB)
        outputs = [ ]
        state = self.initial_state
        with tf.variable_scope('RNN'):
            for time_step in range(num_steps):
                if time_step > 0:
                    tf.get_variable_scope().reuse_variables()
                cell_output, state = cell(inputs[:, time_step, :], state)
                outputs.append(cell_output)
        self.final_state = state
        # batchsize * (HIDDEN_SIZE * num_steps)
        # () * HIDDEN_SIZE
        output = tf.reshape(tf.concat(outputs, axis = 1), [-1, HIDDEN_SIZE])
        weight = tf.get_variable(
            'weight',
            [HIDDEN_SIZE, VOCAB_SIZE]
        )
        bias = tf.get_variable(
            'bias',
            [VOCAB_SIZE]
        )
        logits = tf.matmul(output, weight) + bias
        loss = tf.contrib.legacy_seq2seq.sequence_loss_by_example(
            [logits],
            [tf.reshape(self.targets, [-1])],
            [tf.ones([ batch_size * num_steps ], dtype = tf.float32)]
        )
        self.cost = tf.reduce_sum(loss) / batch_size
        
        if not is_training: return
        trainable_variables = tf.trainable_variables()
        grads, _ = tf.clip_by_global_norm(
            tf.gradients(self.cost, trainable_variables),
            MAX_GRAD_NORM
        )
        self.train_op = tf.train.GradientDescentOptimizer(LEARNING_RATE).apply_gradients(
            zip(grads, trainable_variables)
        )

def run_epoch(session, model, data, train_op, output_log):
    total_costs = 0.0
    iters = 0
    true_initial_state = session.run(model.initial_state)
    step = 0
    batch = reader.ptb_producer(data, model.batch_size, model.num_steps)
    coordinator = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord = coordinator)
    while step < TOTAL_STEPS:
        x, y = session.run(batch)
        cost, state, _ = session.run([ model.cost, model.final_state, model.train_op ], feed_dict = {
            model.input_data: x,
            model.targets: y,
            model.initial_state: true_initial_state
        })
        total_costs += cost
        iters += model.num_steps
        if output_log and not step % 50:
            print('After {} steps, perplexity is {:.4f}'.format(step, np.exp(total_costs / float(iters))))
        step += 1
    coordinator.request_stop()
    coordinator.join(threads)
    return np.exp(total_costs / float(iters))

def main():
    train_data, valid_data, test_data, _ = reader.ptb_raw_data(DATA_DIR_NAME)
    initializer = tf.random_uniform_initializer(-0.5, 0.5)
    with tf.variable_scope('language_model', reuse = None, initializer = initializer):
        train_model = PTBModel(True, TRAIN_BATCH_SIZE, TRAIN_NUM_STEPS)
    with tf.variable_scope('language_model', reuse = True, initializer = initializer):
        eval_model = PTBModel(False, EVAL_BATCH_SIZE, EVAL_NUM_STEPS)
    with tf.Session() as session:
        tf.global_variables_initializer().run()
        for i in range(NUM_EPOCH):
            print('NOW IN {} ITERRATION'.format(i + 1))
            run_epoch(session, train_model, train_data, train_model.train_op, True)

            valid_perplexity = run_epoch(session, eval_model, valid_data, tf.no_op(), False)
            print('{} ITERATION: VALIDATING PERPLEXITY {:.4f}'.format(i + 1, valid_perplexity))
        test_perplexity = run_epoch(session, eval_model, test_data, tf.no_op(), False)
        print('FINAL TESTING PERPLEXITY {:.4f}'.format(test_perplexity))

if __name__ == '__main__':
    main()