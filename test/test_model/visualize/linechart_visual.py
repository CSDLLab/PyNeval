import re
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import shutil
import os
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


def linechar_visual(avgs, stds, lables=None, file_name=None, num=100):
    if lables is None:
        lables = ['line1', 'line2', 'line3', 'line4']
    it = ["{}%".format(i*10) for i in range(len(avgs[0]))]
    stdx = [0, 10]
    stdy = [1, 0]

    colors = ['#FF3030', '#FF8C00', '#4876FF', '#458B00']
    for i in range(len(avgs)):
        f, ax = plt.subplots(1, 1)
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

        ax.plot(stdx, stdy, "#000000", linestyle="--")
        plt.show()
    # f.savefig(os.path.join('./out_image', lables[i]+file_name), dpi=500)


if __name__ == "__main__":
    avgs, stds = read_data(".\input_data\lm_delete_recall.txt")
    # linechar_visual(avgs, stds, lables=['2_18','30_18_10','34_23_10'], file_name='lm_delete_recall.png')
    linechar_visual(avgs, stds, lables=['diadem_example', '30_18_10_gold','34_23_10'], file_name='lm_delete_precition.png', num=100)
