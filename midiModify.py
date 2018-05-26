from midiDealing import *
import os

FREQ_LIST = [16.352, 17.324, 18.354, 19.445, 20.602, 21.827, 23.125, 24.5, 25.957, 27.5, 29.135, 30.868]
MUSIC_FILE = "out.mid"
MUSIC_DIR = os.getcwd()


class MidiModify:
    def __init__(self, file_name, v, a, bpm):
        self.file_name = file_name
        # print("v:", v, "a:", a)
        self.v = v
        self.a = a
        self.bpm = bpm

    def dealing(self):
        if os.path.isfile(MUSIC_FILE):
            song = read_one_file(MUSIC_DIR, MUSIC_FILE, False)
            # print(song)
            song = np.array(song)
            # print(song)
            cnt = 0
            # time = song[len(song) - 1, 0]
            k = len(song) - 1
            while k > 0:
                song[k, 0] = song[k, 0] - song[k - 1, 0]
                k = k - 1
            for k in range(len(song) - 1):
                # song[k, 0] = song[k, 0] - song[k-1, 0]
                if song[k, 0] == 0:
                    cnt = cnt + 1
            # note_len = time / (len(song) - cnt)
            # print("note number:%f" % (note_len / self.bpm))
            # for k in range(len(song) - 1):
            #     if song[k, 0] * 1 - 0.05 * (self.a - 5) > 0:
            #         song[k, 0] = song[k, 0] * 1 - 0.05 * (self.a - 5)
            #         song[k, 1] = song[k, 1] * 1 - 0.05 * (self.a - 5)

            song[len(song) - 1, 0] = 0
            # for k in range(len(song) - 1):
            #     if song[k, 0] * 1 - 0.05 * (self.a - 5) > 0:
            #         song[k, 0] = song[k, 0] * 1 - 0.05 * (self.a - 5)
            #         song[k, 1] = song[k, 1] * 1 - 0.05 * (self.a - 5)
            print(song)
            print("v:", self.v, "a: ", self.a)
            # if self.a >= 7 and self.bpm <= 120:
            #     self.bpm = self.bpm*1.5
            v = self.v
            while self.v > 5:
                # song = upper(song)
                self.v = self.v - 1
            self.v = v
            while self.v < 5:
                # song = lower(song)
                # song = lower(song)
                # song = lower(song)
                # song = lower(song)
                if self.bpm > 90 and self.a < 5:
                    self.bpm = self.bpm - 10
                self.v = self.v + 1
            res = save_data(self.file_name, song, self.bpm)
            return res


def upper(s):
    for k in range(len(s) - 1):
        flag = 0
        # print(k)
        for i in range(9):
            if flag == 0:
                for j in range(len(FREQ_LIST)):
                    if FREQ_LIST[j]*2**(i+1) - 0.8 < s[k][2] < FREQ_LIST[j]*2**(i+1) + 0.8:
                        if j == len(FREQ_LIST) - 1:
                            s[k][2] = 2**(i + 2) * FREQ_LIST[j]
                            flag = 1
                            break
                        else:
                            s[k][2] = FREQ_LIST[j + 1]*2**(i+1)
                            flag = 1
                            break
    return s


def lower(s):
    for k in range(len(s) - 1):
        flag = 0
        for i in range(9):
            if flag == 0:
                for j in range(len(FREQ_LIST)):
                    # print(FREQ_LIST[j]*2**(i+1) - 0.8)
                    if FREQ_LIST[j]*(2**(i+1)) - 0.8*i < s[k][2] < FREQ_LIST[j]*(2**(i+1)) + 0.8*i:
                        # print("y:", s[k][2])
                        if j == 0 and i > 0:
                            s[k][2] = (2**i) * FREQ_LIST[len(FREQ_LIST) - 1]
                            flag = 1
                            break
                        elif j != 0:
                            s[k][2] = FREQ_LIST[j - 1]*(2**(i+1))
                            flag = 1
                            break
    return s
