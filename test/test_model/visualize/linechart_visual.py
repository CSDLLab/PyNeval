import re
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import shutil
import os
import csv
import math
sns.set_style('whitegrid')


def read_data(file_path):
    xs, ys = [], []
    fg = 0
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line[0] == '#':
                continue
            print(line.split())
            v = list(map(float, line.split()))
            x_y = list()
            for item in v:
                x_y.append(item)
            if fg == 0:
                xs.append(x_y)
            else:
                ys.append(x_y)
            fg = 1 - fg
    return xs, ys


def linechar_visual(avgs, stds, output_dir, lables=None, file_name=None):
    if lables is None:
        lables = ['line1', 'line2', 'line3', 'line4']
    it = ["{}%".format((i+1)*10) for i in range(len(avgs[0]))]

    colors = ['#FF3030', '#FF8C00', '#4876FF', '#458B00']
    f, ax = plt.subplots(1, 1)
    # plt.xlim(it[0], it[-1])

    for i in range(len(avgs)):
        ax.plot(it, avgs[i], color=colors[i], label=lables[i])
        r1 = list(map(lambda x: x[0]-x[1]*2, zip(avgs[i], stds[i])))
        r2 = list(map(lambda x: x[0]+x[1]*2, zip(avgs[i], stds[i])))
        r3 = list(map(lambda x: x[0]-x[1], zip(avgs[i], stds[i])))
        r4 = list(map(lambda x: x[0]+x[1], zip(avgs[i], stds[i])))
        ax.fill_between(it, r1, r2, color=colors[i], alpha=0.1)
        ax.fill_between(it, r3, r4, color=colors[i], alpha=0.3)
        ax.legend()

        ax.set_xlabel('moved node number')
        ax.set_ylabel('score')

    plt.show()
    f.savefig(os.path.join(output_dir, file_name), dpi=500)


if __name__ == "__main__":
    # avgs, stds = read_data(".\input_data\lm_delete_recall.txt")
    # lables = ['diadem_example', '30_18_10_gold', '34_23_10']
    # output_dir = "../../../output/csv_dir"
    # fig_name = 'lm_delete_precition.png'
    # # linechar_visual(avgs, stds, lables=['2_18','30_18_10','34_23_10'], file_name='lm_delete_recall.png')
    # linechar_visual(avgs, stds, lables=lables, file_name=fig_name, )

    # root csv fold for input files
    data_dir = "../../../data/csv_data"
    # fold for output png
    output_dir = "../../../output/csv_dir"

    # select result on different swc files
    for file_name in os.listdir(data_dir):
        file_dir = os.path.join(data_dir, file_name)
        # select result on different metric method
        for method in os.listdir(file_dir):
            method_dir = os.path.join(file_dir, method)
            # there are two ways to generate random data: delete and move_5
            delete_dir = os.path.join(method_dir, "delete")
            move_dir = os.path.join(method_dir, "fake_data.txt")
            stds = []
            avgs = []
            with open(move_dir) as f:
                reader = csv.reader(f)
                fg = 0
                for row in reader:
                    row = list(map(float, row))
                    if fg == 0:
                        avgs.append(row)
                    else:
                        stds.append(row)
                    fg ^= 1

            linechar_visual(avgs=avgs, stds=stds, output_dir=output_dir, file_name=file_name+"move_5")
