from __future__ import print_function
import tensorflow as tf
import pickle as pkl

import os
from six.moves import cPickle
import re
import random

from model import Model

happy = pkl.load(open('generation/happy', "rb"))
happy_bpm = pkl.load(open('generation/happy_bpm', "rb"))
sad = pkl.load(open('generation/sad', "rb"))
sad_bpm = pkl.load(open('generation/sad_bpm', "rb"))
calm = pkl.load(open('generation/calm', "rb"))
calm_bpm = pkl.load(open('generation/calm_bpm', "rb"))
angry = pkl.load(open('generation/angry', "rb"))
angry_bpm = pkl.load(open('generation/angry_bpm', "rb"))


class Generation:
    def __init__(self, file_name, v, a):
        self.file_name = file_name
        self.valence = v
        self.arousal = a
        if v < 5:
            self.save_dir = "./model_sad_angry"
        elif v > 5 and a > 5:
            self.save_dir = "./model_happy"
        else:
            self.save_dir = "./model"
        self.n = 500
        self.prime, self.bpm = self.calculate(v, a)
        self.raw = ""
        with open(os.path.join(self.save_dir, 'config.pkl'), 'rb') as f:
            saved_args = cPickle.load(f)
        with open(os.path.join(self.save_dir, 'chars_vocab.pkl'), 'rb') as f:
            self.chars, self.vocab = cPickle.load(f)
        self.model = Model(saved_args, training=False)

    def setFileName(self, file_name):
        self.file_name = file_name

    def calculate(self, v, a):
        self.valence = v
        self.arousal = a
        if v > 5 and a > 5:
            list_h = [i for i in range(len(happy))]
            num = random.sample(list_h, 1)[0]
            s = happy[num]
            bpm = happy_bpm[num]
        elif v < 5 and a < 5:
            list_h = [i for i in range(len(sad))]
            num = random.sample(list_h, 1)[0]
            s = sad[num]
            bpm = sad_bpm[num]
        elif v < 5 and a > 5:
            list_h = [i for i in range(len(angry))]
            num = random.sample(list_h, 1)[0]
            s = angry[num]
            bpm = angry_bpm[num]
        else:
            list_h = [i for i in range(len(calm))]
            num = random.sample(list_h, 1)[0]
            s = calm[num]
            bpm = calm_bpm[num]
        return s, bpm

    def sample(self):
        with tf.Session() as sess:
            tf.global_variables_initializer().run()
            saver = tf.train.Saver(tf.global_variables())
            ckpt = tf.train.get_checkpoint_state(self.save_dir)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)
                self.raw = self.model.sample(sess, self.chars, self.vocab, self.n, self.prime,
                                   1).encode('utf-8')

    def deal_abc(self):
        print(self.raw)
        t = str(self.raw)
        # idx = t.index('@X:')
        # print(idx)
        # text = t[2:idx]
        text = t[2:]
        strinfo = re.compile('@')
        abc = strinfo.sub('\n', text)
        p = os.getcwd()
        f = open(p+'/tmp.abc', 'w')

        f.write(abc)
        f.close()
        os.system("abc2midi "+p+"/tmp.abc -o "+self.file_name)
        os.remove(p+'/tmp.abc')