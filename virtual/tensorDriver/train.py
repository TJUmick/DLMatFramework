import os
import tensorflow as tf
import driving_data
import model

LOGDIR = './save'

sess = tf.InteractiveSession()

L2NormConst = 0.001

# Get all model "parameters" that are trainable
train_vars = tf.trainable_variables()

# Loss is mean squared error plus l2 regularization
# model.y (Model output), model.y_(Labels)
# tf.nn.l2_loss: Computes half the L2 norm of a tensor without the sqrt
# output = sum(t ** 2) / 2
with tf.name_scope("MeanSquared_Loss_L2_Reg"):
    loss = tf.reduce_mean(tf.square(tf.subtract(model.y_, model.y))) + tf.add_n([tf.nn.l2_loss(v) for v in train_vars]) * L2NormConst

# Solver configuration
with tf.name_scope("Solver"):
    train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)

# Initialize all random variables (Weights/Bias)
sess.run(tf.global_variables_initializer())

# create a summary to monitor cost tensor
tf.summary.scalar("loss", loss)
# merge all summaries into a single op
merged_summary_op = tf.summary.merge_all()

saver = tf.train.Saver()

# op to write logs to Tensorboard
logs_path = './logs'
summary_writer = tf.summary.FileWriter(logs_path, graph=tf.get_default_graph())

epochs = 30
batch_size = 100

# train over the dataset about 30 times
for epoch in range(epochs):
  for i in range(int(driving_data.num_images/batch_size)):
    xs, ys = driving_data.LoadTrainBatch(batch_size)
    #train_step.run(feed_dict={model.x: xs, model.y_: ys, model.keep_prob: 0.8})
    train_step.run(feed_dict={model.x: xs, model.y_: ys})
    if i % 10 == 0:
      xs, ys = driving_data.LoadValBatch(batch_size)
      #loss_value = loss.eval(feed_dict={model.x:xs, model.y_: ys, model.keep_prob: 1.0})
      loss_value = loss.eval(feed_dict={model.x:xs, model.y_: ys})
      print("Epoch: %d, Step: %d, Loss: %g" % (epoch, epoch * batch_size + i, loss_value))

    # write logs at every iteration
    #summary = merged_summary_op.eval(feed_dict={model.x:xs, model.y_: ys, model.keep_prob: 1.0})
    summary = merged_summary_op.eval(feed_dict={model.x:xs, model.y_: ys})
    summary_writer.add_summary(summary, epoch * batch_size + i)

    if i % batch_size == 0:
      if not os.path.exists(LOGDIR):
        os.makedirs(LOGDIR)
      checkpoint_path = os.path.join(LOGDIR, "model.ckpt")
      filename = saver.save(sess, checkpoint_path)
  print("Model saved in file: %s" % filename)

print("Run the command line:\n" \
          "--> tensorboard --logdir=./logs " \
          "\nThen open http://0.0.0.0:6006/ into your web browser")