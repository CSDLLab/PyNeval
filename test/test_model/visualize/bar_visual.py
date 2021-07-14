import matplotlib.pyplot as plt
import numpy as np

data = [5, 20, 15, 25, 10]


def bar_visual():
    size = 4
    x = np.arange(size)

    a = [0.6842, 0.7117, 0.6550, 0.6740]
    b = [0.6814, 0.7126, 0.6539, 0.6741]
    c = [0.6684, 0.7099, 0.6590, 0.6650]
    d = [0.6740, 0.7029, 0.6558, 0.6638]
    e = [0.6563, 0.6965, 0.6080, 0.6386]

    total_width, n = 0.6, 5
    width = total_width / n
    x = x - (total_width - width) / 2

    ax = plt.axes()

    plt.ylim(0.6, 0.72)
    plt.xticks([0, 1, 2, 3], ["2816 21504", "2816 22016", "2304 21504", "2304 22016"])
    plt.xlabel("Filenames of test data")
    plt.ylabel("Average value of SSD recall and precision")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.bar(x, a, width=width, label='best parameter for 2816 21504', color=['#63B2EE'])
    plt.bar(x + width, b, width=width, label='best parameter for 2816 22016', color=['#76DA91'])
    plt.bar(x + 2 * width, c, width=width, label='best parameter for 2304 21504', color=['#F8CB7f'])
    plt.bar(x + 3 * width, d, width=width, label='best parameter for 2304 22016', color=['#F89588'])
    plt.bar(x + 4 * width, e, width=width, label='default', color=['#9192AB'])

    plt.legend()
    plt.show()


if __name__ == "__main__":
    bar_visual()
