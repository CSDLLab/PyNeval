import matplotlib.pyplot as plt
import numpy as np

data = [5, 20, 15, 25, 10]


def bar_visual():
    size = 4
    x = np.arange(size)

    a = [0.8044, 0.8312, 0.7218, 0.7527]
    b = [0.8021, 0.8354, 0.7358, 0.7537]
    c = [0.7899, 0.8335, 0.7326, 0.7318]
    d = [0.8039, 0.8318, 0.7367, 0.7588]
    e = [0.7825, 0.8192, 0.6796, 0.7310]

    total_width, n = 0.6, 5
    width = total_width / n
    x = x - (total_width - width) / 2

    ax = plt.axes()

    plt.ylim(0.66, 0.86)
    plt.xticks([0, 1, 2, 3], ["FM3", "FM4", "FM5", "FM6"])
    plt.xlabel("Test data")
    plt.ylabel("F1 score of SSD metric")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.bar(x, [0, 0, 0, 0], width=width, edgecolor="k", label='self optimization', color='white')

    plt.bar(x, a, width=width, label='cross optimization', edgecolor="k", color='white', hatch='...')
    plt.bar(x + 1 * width, b, width=width, edgecolor="k", color='white', hatch='...')
    plt.bar(x + 2 * width, c, width=width, edgecolor="k", color='white', hatch='...')
    plt.bar(x + 3 * width, d, width=width, edgecolor="k", color='white', hatch='...')
    plt.bar(x + 4 * width, e, width=width, label='default', edgecolor="k", color='white', hatch='//')

    plt.bar(x, [0.8044, 0, 0, 0], width=width, edgecolor="k", color='white')
    plt.bar(x + 1 * width, [0, 0.8354, 0, 0], width=width, edgecolor="k", color='white')
    plt.bar(x + 2 * width, [0, 0, 0.7326, 0], width=width, edgecolor="k", color='white')
    plt.bar(x + 3 * width, [0, 0, 0, 0.7588], width=width, edgecolor="k", color='white')

    plt.legend()
    plt.show()


if __name__ == "__main__":
    bar_visual() 
