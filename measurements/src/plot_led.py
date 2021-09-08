#!/usr/bin/env python3

import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter

import argparse
import itertools
import numpy as np
import os
import pylab
import seaborn as sns
import sys

import base

from colorpy import ciexyz
from colorpy import colormodels


def main(inputs, output, colors):

    highlight, bi = base.init()
    if len(inputs) <= 1:
        _, ax = base.create_figure(6, 3)
    else:
        _, ax = base.create_figure(6, 2)

    xlim = (300, 700) if len(inputs) > 1 else None
    ymax = np.NINF

    for fname, highlight in itertools.zip_longest(inputs, colors):
        x = np.loadtxt(fname)
        Y = x[:, 1]
        x = x[:, 0]
        ymax = max(Y.max(), ymax)

        if xlim:
            i = np.argwhere(np.logical_and(xlim[0] <= x, x <= xlim[1]))
            Y = Y[i].flatten()
            x = x[i].flatten()

        a = np.trapz(Y)
        mean = np.dot(x, Y / a)

        if highlight is None:
            xyz = ciexyz.xyz_from_wavelength(mean)
            highlight = colormodels.irgb_string_from_xyz(xyz)

        if xlim:
            delta = x[1] - x[0]
            x = np.hstack(([xlim[0], x[0] - delta], x,
                           [x[-1] + delta, xlim[1]]))
            Y = np.hstack(([0, 0], Y, [0, 0]))

        plt.plot(x, Y, color=highlight)

    if xlim:
        plt.xlim(xlim)

    plt.xlabel("Wavelength (nm)")
    plt.ylim(None, (ymax *2 //1 +1) /2)
    plt.ylabel("Voltage (V)", labelpad=9)

    base.finalize(None, bi)

    #pylab.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
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
                        help="the colors to be used for the LED plots.")

    args = parser.parse_args()
    sys.exit(main(args.data, args.output, args.colors))
