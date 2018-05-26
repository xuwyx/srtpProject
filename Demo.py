import numpy as np
import pickle as pkl
import time
from keras import models

# model_A = models.load_model("model_a")
# model_V = models.load_model("model_v")

class Classification:
    def __init__(self, csvName):
        self.data_x_file = csvName
        self.batch_size = 64
        self.mean = pkl.load(open("classification/mean", "rb"))
        self.std = pkl.load(open("classification/std", "rb"))
        self.model_A = models.load_model("model_a")
        self.model_V = models.load_model("model_v")
        self.valance = 0
        self.arousal = 0

    def run(self):
        my_matrix = np.loadtxt(open(self.data_x_file, "rb"), delimiter=';', skiprows=1)
        my_matrix = np.delete(my_matrix, 0, 1)
        print(my_matrix.shape)
        data_x = []
        if len(my_matrix) < 120*5:
            print("The song is too short, we need a song with at least 120 seconds.")
            return 0
        list_ma = [j for j in range(0, 76) if j % 5 == 0]
        for i in range(self.batch_size):
            # data_x.append(my_matrix[15+i*5:31+i*5, :])
            data_x.append(my_matrix[list_ma, :])
            list_ma = [x + 5 for x in list_ma]
            # if i < 40:
            #     data_x.append(my_matrix[76 + 16 * i:92 + 16 * i, :])
            # else:
            #     data_x.append(my_matrix[716:732, :])
        # data_x.append(my_matrix[76:292, :])
        # data_x -= np.mean(data_x, axis=0)
        # data_x /= np.std(data_x, axis=0)
        data_x -= self.mean
        data_x /= self.std
        data_x = np.array(data_x)
        print(data_x.shape)
        data_x = data_x[0:64][:, :]
        classes_V = self.model_V.predict(data_x, batch_size=self.batch_size)
        classes_A = self.model_A.predict(data_x, batch_size=self.batch_size)
        # classes_V = self.model_V.predict_on_batch(data_x)
        # classes_A = self.model_A.predict_on_batch(data_x)
        self.valance = np.mean(classes_V)*10
        self.arousal = np.mean(classes_A)*10
        # self.valance = classes_V[0] * 10
        # self.arousal = classes_A[0] * 10

        return 1

    def set_file_name(self, csvName):
        self.data_x_file = csvName
