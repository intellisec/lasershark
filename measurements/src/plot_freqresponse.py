#!/usr/bin/env python3

import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt

import argparse
import csv
import itertools
import numpy as np
import os
import seaborn as sns
import sys

import base


def main(inputs, output, colors):

    def convert(b):
        return float(b.replace(',', '.'))

    def read(fname, skiprows=0):
        with open(fname, 'r') as f:
            for line in csv.reader(f, delimiter=',', quotechar='"'):
                if skiprows == 0:
                    yield [convert(x) for x in line]
                else:
                    skiprows -= 1

    c, bi = base.init()
    _, ax = base.create_figure(6, 3)

    for fname, c in itertools.zip_longest(inputs, colors):
        x = np.array(list(read(fname, skiprows=2)))
        Y = x[:, 1]
        x = x[:, 0]

        plt.plot(x, Y, color=c)

    plt.xlabel("Frequency (kHz)")
    plt.xlim(0, 300)
    plt.ylabel("Power (dBm)")
    

    base.finalize(None, bi)
    plt.tight_layout()

    base.save_figure(output)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("data", metavar="TSV", action="store", type=str, nargs="+",
                        help="the data to plot.")
    parser.add_argument("output", metavar="OUT", action="store", type=str,
                        help="the file to plot to. This also specifies the output type.")
    parser.add_argument("--colors", action="store", nargs="+", default=[],
                        help="the colors to be used for the sample rate plots.")

    args = parser.parse_args()
    sys.exit(main(args.data, args.output, args.colors))
