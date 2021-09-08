import itertools
import matplotlib.pyplot as plt
import seaborn as sns
import sys


def init():
    sns.set_style("whitegrid", {'axes.edgecolor': '0', 'grid.linestyle': ':',
                                'grid.color': '.5', 'legend.frameon': True})
    return 'red', False


def finalize(legend, apply_return_val):
    if apply_return_val:
        if legend != None:
            f = legend.get_frame()
            f.set_facecolor('white')
            f.set_alpha(1)

        sns.despine(offset=5)

        ax = plt.gca()
        ax.yaxis.grid(True)
        for line in ax.get_ygridlines():
            line.set_linewidth(0.5)


def combine_styles(colors, linestyles):
    linestyles = list(itertools.chain(
        *map(lambda x: [x] * len(colors), linestyles)))

    def gen():
        c = colors
        for i in range(len(linestyles) / len(c)):
            yield c
            c = c[::-1]

    colors = list(itertools.chain(*gen()))

    return colors, linestyles


def create_figure(width=5, height=3):
    plt.clf()
    fig = plt.figure(figsize=(width, height))
    ax = plt.gca()
    return fig, ax


def save_figure(output):
    if output.split('.')[-1] == 'tex':
        from matplotlib2tikz import save as tikz_save
        tikz_save(output)

    else:
        plt.savefig(output)
