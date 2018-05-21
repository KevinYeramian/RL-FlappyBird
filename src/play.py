import tensorflow as tf
import cv2
import sys
import random
import numpy as np
from collections import deque
from ple.games.flappybird import FlappyBird
from ple import PLE
from config import *
from model import Network
import prepossessing


def play():
    sess = tf.InteractiveSession()

    net = Network()

    # open up a game state to communicate with emulator
    game = FlappyBird()
    p = PLE(game, fps=30, display_screen=True)
    p.init()
    reward = 0.0

    # get the first state by doing nothing and preprocess the image to 80x80x4

    actions = p.getActionSet()
    p.act(actions[1])

    s_t = prepossessing.transform_image(p.getScreenRGB())

    saver = tf.train.Saver()
    sess.run(tf.initialize_all_variables())
    checkpoint = tf.train.get_checkpoint_state("../saved_networks")
    if checkpoint and checkpoint.model_checkpoint_path:
        saver.restore(sess, checkpoint.model_checkpoint_path)
        print("Successfully loaded:", checkpoint.model_checkpoint_path)
    else:
        print("Could not find old network weights")

    # start training
    t = 0
    while t < MAX_ITE:
        if p.game_over():
            p.reset_game()
            terminal = True
        else:
            terminal = False

        # choose an action epsilon greedily
        readout_t = net.readout.eval(feed_dict={net.s: [s_t]})[0]
        a_t = np.zeros([ACTIONS])

        action_index = np.argmax(readout_t)
        a_t[action_index] = 1

        # run the selected action and observe next state and reward
        action = int(np.argmax(a_t))
        if action == 0:
            action = 1
        else:
            action = 0
        r_t = p.act(actions[action])

        s_t1 = prepossessing.transform_image_stacked(p.getScreenRGB(), s_t)

        # update the old values
        s_t = s_t1
        t += 1

        print("TIMESTEP", t, "/ ACTION", action_index,
              "/ REWARD", r_t, "/ Q_MAX %e" % np.max(readout_t))


if __name__ == "__main__":
    play()