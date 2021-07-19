import matplotlib.pyplot as plt
import numpy as np

data = [5, 20, 15, 25, 10]


def bar_visual():
    size = 4
    x = np.arange(size)

    a = [0.6842, 0.7117, 0.6550, 0.6019]
    b = [0.6814, 0.7126, 0.6539, 0.6004]
    c = [0.6684, 0.7099, 0.6590, 0.5969]
    d = [0.6740, 0.7029, 0.6558, 0.6083]
    e = [0.6563, 0.6965, 0.6080, 0.5872]

    total_width, n = 0.6, 5
    width = total_width / n
    x = x - (total_width - width) / 2

    ax = plt.axes()

    plt.ylim(0.58, 0.72)
    plt.xticks([0, 1, 2, 3], ["2816 21504", "2816 22016", "2304 21504", "2304 22016"])
    plt.xlabel("Filenames of test data")
    plt.ylabel("Average value of SSD recall and precision")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.bar(x, [0, 0, 0, 0], width=width, label='best performance', color='black')

    plt.bar(x, a, width=width, label='other performance', edgecolor="k", color='white', hatch='//')
    plt.bar(x + 1 * width, b, width=width, edgecolor="k", color='white', hatch='//')
    plt.bar(x + 2 * width, c, width=width, edgecolor="k", color='white', hatch='//')
    plt.bar(x + 3 * width, d, width=width, edgecolor="k", color='white', hatch='//')
    plt.bar(x + 4 * width, e, width=width, label='default', edgecolor="k", color='white', hatch='...')

    plt.bar(x, [0.6842, 0, 0, 0], width=width, color='black')
    plt.bar(x + 1 * width, [0, 0.7126, 0, 0], width=width, color='black')
    plt.bar(x + 2 * width, [0, 0, 0.6590, 0], width=width, color='black')
    plt.bar(x + 3 * width, [0, 0, 0, 0.6083], width=width, color='black')

    plt.legend()
    plt.show()


if __name__ == "__main__":
    bar_visual() 
