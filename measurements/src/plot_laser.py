#!/usr/bin/env python3

import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter

import argparse
import numpy as np
import os
import pylab
import seaborn as sns
import sys

import base 

from colorpy import ciexyz
from colorpy import colormodels


def main(inputs, output):

    highlight, bi = base.init()
    if len(inputs) <= 1:
        _, ax = base.create_figure(6, 3)
    else:
        _, ax = base.create_figure(6, 2)

    xlim = (300, 700) if len(inputs) > 1 else None

    for fname in inputs:
        x = np.loadtxt(fname)
        Y = x[:, 1]
        x = x[:, 0]

        max_wl = x[np.argmax(Y)]

        xyz = ciexyz.xyz_from_wavelength(max_wl)
        highlight = colormodels.irgb_string_from_xyz(xyz)

        plt.plot(x, Y, color=highlight)

    if xlim:
        plt.xlim(xlim)

    plt.xlabel("Wavelength (nm)")

    plt.ylim(None, 0)
    plt.ylabel("Power (dBm)")

    base.finalize(None, bi)

    #pylab.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.tight_layout()

    base.save_figure(output)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("data", metavar="TSV", action="store", type=str, nargs="+",
                        help="The data to plot.")
    parser.add_argument("output", metavar="OUT", action="store", type=str,
                        help="The file to plot to. This also specifies the output type.")

    args = parser.parse_args()
    sys.exit(main(args.data, args.output))
