#!/usr/bin/env python3

import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt

import argparse
import itertools
import numpy as np
import os
import seaborn as sns
import sys

import base


def main(inputs, output, colors):

    def convert(b):
        return float(b.replace(b',', b'.').replace(b'--', b'NaN'))

    c, bi = base.init()
    _, ax = base.create_figure(4, 3)
    xlim = 0

    for fname, c in itertools.zip_longest(inputs, colors):
        if fname == None:
            break

        x = np.loadtxt(fname, converters={0: convert, 1: convert})
        Y = x[:, 1]
        x = x[:, 0]
        xlim = max(x.max(), xlim)

        label, _ = os.path.splitext(os.path.basename(fname))

        plt.plot(x, Y, color=c, label=label)
        plt.legend()

    plt.xlabel("Frequency (MHz)")
    print(xlim)
    plt.xlim(0, np.round(xlim))

    plt.ylabel("Normalized Power (dBm)")
    plt.ylim(-50, 0)
    

    base.finalize(None, bi)
    plt.tight_layout()

    base.save_figure(output)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("data", metavar="CSV", action="store", type=str, nargs="+",
                        help="the data to plot.")
    parser.add_argument("output", metavar="OUT", action="store", type=str,
                        help="the file to plot to. This also specifies the output type.")
    parser.add_argument("--colors", action="store", nargs="+", default=[],
                        help="the colors to be used for the sample rate plots.")

    args = parser.parse_args()
    sys.exit(main(args.data, args.output, args.colors))
