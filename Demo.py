import numpy as np
import pickle as pkl
import sys
from keras import models
import matplotlib.pyplot as plt

class Classification:
    def __init__(self, csvName):
        self.data_x_file = csvName
        self.batch_size = 64
        self.mean = pkl.load(open("mean", "rb"))
        self.std = pkl.load(open("std", "rb"))
        self.model_A = models.load_model("model_adagrad_A_103")
        self.model_V = models.load_model("model_adagrad_V_102")
        self.valance = 0
        self.arousal = 0
    def run(self):
        my_matrix = np.loadtxt(open(self.data_x_file, "rb"), delimiter=';', skiprows=1)
        my_matrix = np.delete(my_matrix, 0, 1)
        data_x = []
        if (len(my_matrix) < 218 + 75):
            print("The song is too short, we need a song with at least 60 seconds.")
            return 0
        for i in range(self.batch_size):
            data_x.append(my_matrix[76:292, :])
        data_x -= self.mean
        data_x /= self.std

        classes_V = self.model_V.predict(data_x[0:64, :, :], batch_size=self.batch_size)
        classes_A = self.model_A.predict(data_x[0:64, :, :], batch_size=self.batch_size)
        self.valance = (classes_V[0] - 0.5) * 1.2 + 0.5
        self.arousal = (classes_A[0] - 0.5) * 1.2 + 0.5
        return 1