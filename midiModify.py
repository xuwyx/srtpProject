from midiDealing import *
import os
FREQ_LIST = [16.352, 17.324, 18.354, 19.445, 20.602, 21.827, 23.125, 24.5, 25.957, 27.5, 29.135, 30.868]
MUSIC_FILE = "out.mid"
SAVE_FILE = "out1.mid"
MUSIC_DIR = os.getcwd()
v = 4
a = 6


def upper(s):
    for k in range(len(s) - 1):
        flag = 0
        for i in range(9):
            if flag == 0:
                for j in range(len(FREQ_LIST) - 1):
                    if FREQ_LIST[j] - 0.8 < s[k, 2] < FREQ_LIST[j] + 0.8:
                        if j == len(FREQ_LIST) - 1:
                            s[k, 2] = (i+2) * FREQ_LIST[j]
                            flag = 1
                            break
                        else:
                            s[k, 2] = FREQ_LIST[j + 1]
                            break
    return s


def lower(s):
    for k in range(len(s) - 1):
        flag = 0
        for i in range(9):
            if flag == 0:
                for j in range(len(FREQ_LIST) - 1):
                    if FREQ_LIST[j] - 0.8 < s[k, 2] < FREQ_LIST[j] + 0.8:
                        if j == 0 and i > 0:
                            s[k, 2] = i * FREQ_LIST[len(FREQ_LIST) - 1]
                            flag = 1
                            break
                        elif j != 0:
                            s[k, 2] = FREQ_LIST[j - 1]
                            break
    return s

if os.path.isfile(MUSIC_FILE):
    song = read_one_file(MUSIC_DIR, MUSIC_FILE, False)
    # print(song)
    song = np.array(song)
    # print(song)
    cnt = 0
    for k in range(len(song) - 1):
        song[k, 0] = song[k + 1, 0] - song[k, 0]
        if song[k, 0] == 0:
            cnt = cnt + 1
    time = song[len(song) - 1, 0]
    note_len = time / (len(song) - cnt)
    print("note number:%f" % note_len)
    song[len(song) - 1, 0] = 0
    for k in range(len(song) - 1):
        song[k, 0] = song[k, 0] * 1 + 0.05 * (a - 5)
    while v > 5:
        song = upper(song)
        v = v - 1
    while v < 5:
        song = lower(song)
        v = v + 1
    save_data(SAVE_FILE, song)

    # print(song.shape)
    # print(song)



