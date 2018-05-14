from __future__ import print_function
import tensorflow as tf

import os
from six.moves import cPickle
import re

from model import Model

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