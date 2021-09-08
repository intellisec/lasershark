#!/usr/bin/env python3

import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt

import argparse
import csv
import itertools
import numpy as np
import seaborn as sns
import sys

import base

from colorpy import ciexyz
from colorpy import colormodels


def main(inputs, output, colors):

    def convert(b):
        return (float(b.replace(',', '.')) if b else None)

    def read(fname, skiprows=0):
        L1, L2 = [], []
        with open(fname, 'r') as f:
            for line in csv.reader(f, delimiter=',', quotechar='"'):
                if skiprows > 0:
                    skiprows -= 1
                else:
                    if line[0]:
                        L1.append([convert(x) for x in line[:2]])
                    else:
                        L2.append([convert(x) for x in line[2:]])

        return L1, L2

    highlight, bi = base.init()
    _, ax = base.create_figure(6, 3)

    for fname in inputs:
        L1, L2 = read(fname, skiprows=3)
        
        def my_filter(L2):
            for x in L2:
                y = [y for y in x[1:] if y > 0]
                if y:
                    yield x[:1] * 2, [0] + y
            

        for X, c in itertools.zip_longest(my_filter(L2), colors):
            x, y = X
            if c is None:
                xyz = ciexyz.xyz_from_wavelength(x[0])
                c= colormodels.irgb_string_from_xyz(xyz)
                    
            plt.plot(x, y, color=c)
                
        x = np.array(L1)
        Y = x[:, 1]
        x = x[:, 0]

        plt.plot(x, Y, color='black')

    plt.xlabel("Wavelength (nm)")
    plt.xlim(200, 1000)
    plt.ylabel("Responsitivity (A/W)", labelpad=9)
    plt.ylim(0, 30)

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
                        help="the colors to be used for the LED plots.")

    args = parser.parse_args()
    sys.exit(main(args.data, args.output, args.colors))
