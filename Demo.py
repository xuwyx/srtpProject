import numpy as np
import pickle as pkl
from keras import models


class Classification:
    def __init__(self, csvName):
        self.data_x_file = csvName
        self.batch_size = 64
        self.mean = pkl.load(open("mean", "rb"))
        self.std = pkl.load(open("std", "rb"))
        self.model_A = models.load_model("model_a")
        self.model_V = models.load_model("model_v")  #8 is better
        self.valance = 0
        self.arousal = 0

    def run(self):
        my_matrix = np.loadtxt(open(self.data_x_file, "rb"), delimiter=';', skiprows=1)
        my_matrix = np.delete(my_matrix, 0, 1)
        print(my_matrix.shape)
        data_x = []
        if (len(my_matrix) < 732):
            print("The song is too short, we need a song with at least 120 seconds.")
            return 0
        for i in range(self.batch_size):
            if i < 40:
                data_x.append(my_matrix[76 + 16 * i:92 + 16 * i, :])
            else:
                data_x.append(my_matrix[716:732, :])
        # data_x.append(my_matrix[76:292, :])
        # data_x -= self.mean
        # data_x /= self.std
        data_x = np.array(data_x)
        print(data_x.shape)
        data_x = data_x[0:64][:, :]
        classes_V = self.model_V.predict(data_x, batch_size=self.batch_size)
        classes_A = self.model_A.predict(data_x, batch_size=self.batch_size)
        self.valance =1 / classes_V[0] * 0.01
        self.arousal = classes_A[0] * 10

        return 1