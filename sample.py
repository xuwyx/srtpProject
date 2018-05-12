from __future__ import print_function
import tensorflow as tf

import argparse
import os
from six.moves import cPickle
import re
import pwd


from model import Model

from six import text_type


class Generation:
    def __init__(self, file_name, v, a):
        self.save_dir = "./model"
        self.file_name = file_name
        self.valence = v
        self.arousal = a
        self.n = 500
        self.prime = self.calculate()
        self.raw = ""

    def calculate(self):
        return "X:001@%7%7@M:"

    def sample(self):
        with open(os.path.join(self.save_dir, 'config.pkl'), 'rb') as f:
            saved_args = cPickle.load(f)
        with open(os.path.join(self.save_dir, 'chars_vocab.pkl'), 'rb') as f:
            chars, vocab = cPickle.load(f)
        model = Model(saved_args, training=False)
        with tf.Session() as sess:
            tf.global_variables_initializer().run()
            saver = tf.train.Saver(tf.global_variables())
            ckpt = tf.train.get_checkpoint_state(self.save_dir)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)
                self.raw = model.sample(sess, chars, vocab, self.n, self.prime,
                                   1).encode('utf-8')

    def deal_abc(self):
        # index = str.index('h')
        print(self.raw)
        t = str(self.raw)
        idx = t.index('@X:')
        print(idx)
        text = t[2:idx]
        strinfo = re.compile('@')
        abc = strinfo.sub('\n', text)
        p = os.getcwd()
        f = open(p+'/tmp.abc', 'w')

        f.write(abc)
        f.close()
        os.system("abc2midi "+p+"/tmp.abc -o "+self.file_name)
        os.remove(p+'/tmp.abc')


# def main():
#     parser = argparse.ArgumentParser(
#                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#     parser.add_argument('--save_dir', type=str, default='save',
#                         help='model directory to store checkpointed models')
#     parser.add_argument('-n', type=int, default=500,
#                         help='number of characters to sample')
#     parser.add_argument('--prime', type=text_type, default=u' ',
#                         help='prime text')
#     parser.add_argument('--sample', type=int, default=1,
#                         help='0 to use max at each timestep, 1 to sample at '
#                              'each timestep, 2 to sample on spaces')
#
#     args = parser.parse_args()
#     sample(args)


# def sample(args):
#     with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
#         saved_args = cPickle.load(f)
#     with open(os.path.join(args.save_dir, 'chars_vocab.pkl'), 'rb') as f:
#         chars, vocab = cPickle.load(f)
#     model = Model(saved_args, training=False)
#     with tf.Session() as sess:
#         tf.global_variables_initializer().run()
#         saver = tf.train.Saver(tf.global_variables())
#         ckpt = tf.train.get_checkpoint_state(args.save_dir)
#         if ckpt and ckpt.model_checkpoint_path:
#             saver.restore(sess, ckpt.model_checkpoint_path)
#             print(model.sample(sess, chars, vocab, args.n, args.prime,
#                                args.sample).encode('utf-8'))