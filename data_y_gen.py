# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pickle as pkl

# read into a dataframe

csv_col = []
label_file = "/Users/xwy/Downloads/annotations/annotations averaged per song/song_level/static_annotations_averaged_songs_1_2000.csv"
label = np.loadtxt(open(label_file, "rb"), delimiter=',', skiprows=1)
print(label.shape)
song_number = np.array(label[:, 0])
label_file = "/Users/xwy/Downloads/annotations/annotations averaged per song/song_level/static_annotations_averaged_songs_2000_2058.csv"
label = np.loadtxt(open(label_file, "rb"), delimiter=',', skiprows=1)
song_number2 = np.array(label[:, 0])
song_number = np.append(song_number, song_number2)
# label_file = "classification/song_id.csv"
# label = pd.read_csv(label_file)
# label = label["song_id"].tolist()

pkl.dump(song_number, open('classification/song_id', "wb"))

data_x = []
# song_number = label  # label[:, 0]

print(len(song_number))


for i in song_number:
    if i % 100 == 0:
        print("Reading " + str(int(i)))
    my_matrix = np.loadtxt(open('/Users/xwy/Downloads/wav/csv2/' + str(int(i)) + '.csv', "rb"), delimiter=';', skiprows=1)
    my_matrix = np.delete(my_matrix, 0, 1)
    list_ma = [j for j in range(0, 16)]
    data_x.append(my_matrix[list_ma, :])
    for k in range(1, 29):  # 1-28 28
        # if k % 5 == 0:
        list_ma = [x + 1 for x in list_ma]
        data_x.append(my_matrix[list_ma, :])  # i from 2 to 56
#
print('data_x shape', (np.array(data_x).shape))
data_x -= np.mean(data_x, axis=0)
data_x /= np.std(data_x, axis=0)
pkl.dump(np.mean(data_x, axis=0), open('classification/mean',"wb"))
pkl.dump(np.std(data_x, axis=0), open('classification/std', "wb"))
pkl.dump(data_x[0:10000, :], open("classification/data_x_new1", "wb"))
pkl.dump(data_x[10000:, :], open("classification/data_x_new2", "wb"))


# data_y
label_file = "classification/arousal.csv"
my_matrix = np.loadtxt(open(label_file, "rb"), delimiter=',', skiprows=1)
my_matrix = np.delete(my_matrix, 0, 1)
data_y_a = []
for i in range(len(my_matrix)):
    line = my_matrix[i]
    for j in range(57): # 0-56 29
        if j % 2 == 0:
            data_y_a.append(line[j])
print('data_y_a shape', np.array(data_y_a).shape)
pkl.dump(data_y_a, open('classification/data_y_a',"wb"))

label_file = "classification/valence.csv"
my_matrix = np.loadtxt(open(label_file, "rb"), delimiter=',', skiprows=1)
my_matrix = np.delete(my_matrix, 0, 1)
data_y_v = []
for i in range(len(my_matrix)):
    line = my_matrix[i]
    for j in range(57):
        if j % 2 == 0:
            data_y_v.append(line[j])
print('data_y_v shape', np.array(data_y_v).shape)
pkl.dump(data_y_v, open('classification/data_y_v',"wb"))

